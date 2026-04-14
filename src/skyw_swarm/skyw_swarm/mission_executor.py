#!/usr/bin/env python3

import json
import re

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from std_msgs.msg import String
from skyw_swarm.action import SetFormation
from skyw_interfaces.srv import DispatchDrone


COLOR_MAP = {
    'kirmizi': 'red',
    'mavi': 'blue',
    'red': 'red',
    'blue': 'blue',
}

FORMATION_MAP = {
    'arrowhead': 'arrow_head',
    'arrow_head': 'arrow_head',
    'line': 'line',
    'v': 'v',
}


class MissionExecutor(Node):

    def __init__(self):
        super().__init__('mission_executor')

        self.declare_parameter('qr_topic', '/qr_decoded')
        self.declare_parameter('drone_ns_prefix', '/drone')
        self.declare_parameter('dispatch_service', 'dispatch')
        self.declare_parameter('dispatch_wait_seconds', 5)
        self.declare_parameter('enable_formation_from_qr', True)
        self.declare_parameter('formation_action', '/set_formation')
        self.declare_parameter('default_formation_type', 'arrow_head')
        self.declare_parameter('default_spacing', 2.0)
        self.declare_parameter('default_altitude', 3.0)
        self.declare_parameter('default_rotation', 0.0)
        self.declare_parameter('default_drone_count', 3)
        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', False)

        self.qr_topic = self.get_parameter('qr_topic').value
        self.drone_ns_prefix = self._normalize_prefix(self.get_parameter('drone_ns_prefix').value)
        self.dispatch_service = self.get_parameter('dispatch_service').value
        self.dispatch_wait_seconds = int(self.get_parameter('dispatch_wait_seconds').value)
        self.enable_formation_from_qr = bool(self.get_parameter('enable_formation_from_qr').value)
        self.formation_action = self.get_parameter('formation_action').value
        self.default_formation_type = self.get_parameter('default_formation_type').value
        self.default_spacing = float(self.get_parameter('default_spacing').value)
        self.default_altitude = float(self.get_parameter('default_altitude').value)
        self.default_rotation = float(self.get_parameter('default_rotation').value)
        self.default_drone_count = int(self.get_parameter('default_drone_count').value)

        self.dispatch_clients = {}
        self.formation_client = ActionClient(self, SetFormation, self.formation_action)

        self.create_subscription(String, self.qr_topic, self._qr_callback, 10)
        self.get_logger().info(f'Mission executor listening on {self.qr_topic}')

    @staticmethod
    def _normalize_prefix(prefix):
        return prefix[:-1] if prefix.endswith('/') else prefix

    @staticmethod
    def _extract_drone_index(value):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            match = re.search(r'(\d+)', value)
            if match:
                return int(match.group(1))
        return None

    def _resolve_drone_name(self, value):
        idx = self._extract_drone_index(value)
        if idx is None or idx <= 0:
            return None
        return idx, f'drone{idx}'

    def _resolve_color(self, value):
        if value is None:
            return None
        key = str(value).strip().lower()
        return COLOR_MAP.get(key)

    def _get_dispatch_client(self, service_name):
        if service_name not in self.dispatch_clients:
            self.dispatch_clients[service_name] = self.create_client(DispatchDrone, service_name)
        return self.dispatch_clients[service_name]

    def _qr_callback(self, msg):
        payload = msg.data.strip()
        if not payload:
            return

        try:
            data = json.loads(payload)
        except json.JSONDecodeError as exc:
            self.get_logger().warn(f'Invalid QR JSON: {exc}')
            return

        self._handle_dispatch(data)
        if self.enable_formation_from_qr:
            self._handle_formation(data)

    def _handle_dispatch(self, data):
        out = data.get('out', {}) if isinstance(data, dict) else {}
        if not out or not bool(out.get('aktif', False)):
            return

        drone_id = out.get('id')
        if drone_id is None:
            drone_id = out.get('uav_id')
        if drone_id is None:
            drone_id = data.get('uav_id')

        resolved = self._resolve_drone_name(drone_id)
        if resolved is None:
            self.get_logger().warn('Dispatch requested but drone id not found.')
            return
        idx, drone_name = resolved

        color = out.get('renk')
        if color is None:
            remove = data.get('remove', {}) if isinstance(data, dict) else {}
            color = remove.get('zone_color')

        target_color = self._resolve_color(color)
        if target_color is None:
            self.get_logger().warn('Dispatch requested but target color is missing or invalid.')
            return

        wait_seconds = out.get('wait_seconds')
        if wait_seconds is None:
            wait_seconds = data.get('wait_time', self.dispatch_wait_seconds)
        wait_seconds = int(wait_seconds)

        service_name = f'{self.drone_ns_prefix}{idx}/{self.dispatch_service}'
        client = self._get_dispatch_client(service_name)

        if not client.wait_for_service(timeout_sec=0.5):
            self.get_logger().warn(f'Dispatch service unavailable: {service_name}')
            return

        req = DispatchDrone.Request()
        req.drone_id = drone_name
        req.target_color = target_color
        req.wait_seconds = wait_seconds

        future = client.call_async(req)
        future.add_done_callback(lambda fut: self._dispatch_result_callback(fut, drone_name))

    def _dispatch_result_callback(self, future, drone_name):
        try:
            response = future.result()
        except Exception as exc:
            self.get_logger().error(f'Dispatch call failed for {drone_name}: {exc}')
            return

        if response.success:
            self.get_logger().info(f'Dispatch accepted for {drone_name}: {response.message}')
        else:
            self.get_logger().warn(f'Dispatch rejected for {drone_name}: {response.message}')

    def _handle_formation(self, data):
        formation = data.get('formation', {}) if isinstance(data, dict) else {}
        if not formation or not bool(formation.get('active', False)):
            return

        formation_type = formation.get('type', self.default_formation_type)
        formation_type = FORMATION_MAP.get(str(formation_type).strip().lower(), self.default_formation_type)

        spacing = float(formation.get('distance', self.default_spacing))

        altitude = self.default_altitude
        altitude_cfg = data.get('altitude')
        if isinstance(altitude_cfg, dict) and bool(altitude_cfg.get('active', False)):
            altitude = float(altitude_cfg.get('value', altitude))

        rotation = float(formation.get('rotation', self.default_rotation))
        drone_count = int(formation.get('drone_count', self.default_drone_count))

        if not self.formation_client.wait_for_server(timeout_sec=0.5):
            self.get_logger().warn('Formation action server not available.')
            return

        goal_msg = SetFormation.Goal()
        goal_msg.formation_type = formation_type
        goal_msg.spacing = spacing
        goal_msg.altitude = altitude
        goal_msg.rotation = rotation
        goal_msg.drone_count = drone_count

        self.get_logger().info(
            f'Sending formation: {formation_type}, spacing={spacing}, altitude={altitude}, '
            f'rotation={rotation}, drones={drone_count}'
        )
        self.formation_client.send_goal_async(goal_msg)


def main():
    rclpy.init()
    node = MissionExecutor()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
