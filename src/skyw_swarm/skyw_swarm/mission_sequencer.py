#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped, Quaternion
from std_msgs.msg import String


def yaw_to_quaternion(yaw: float) -> Quaternion:
    q = Quaternion()
    q.w = math.cos(yaw * 0.5)
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw * 0.5)
    return q


class MissionSequencer(Node):
    """
    High-level mission sequencer for a 3-drone QR scenario.
    - Keeps all drones in offboard by streaming setpoints.
    - Takes off all drones to a shared altitude.
    - Sends drone1 (x500_mono_cam_down) to scan all 6 walls until a decodable QR is found.
    - Controls drone 2 & 3 as followers in a V-formation relative to drone 1.
    """

    def __init__(self):
        super().__init__('mission_sequencer')

        self.declare_parameter('drone_count', 3)
        self.declare_parameter('publish_rate_hz', 20.0)
        self.declare_parameter('takeoff_hold_s', 8.0)
        self.declare_parameter('transit_tolerance_m', 0.5)
        self.declare_parameter('target_hold_s', 15.0)

        # PX4 local frame default is NED, so altitude up is negative Z.
        self.declare_parameter('takeoff_z', -2.5)
        self.declare_parameter('wall_z', -1.0)

        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', False)

        self.drone_count = int(self.get_parameter('drone_count').value)
        self.publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)
        self.takeoff_hold_s = float(self.get_parameter('takeoff_hold_s').value)
        self.transit_tolerance_m = float(self.get_parameter('transit_tolerance_m').value)
        self.target_hold_s = float(self.get_parameter('target_hold_s').value)
        self.takeoff_z = float(self.get_parameter('takeoff_z').value)
        self.wall_z = float(self.get_parameter('wall_z').value)

        self.takeoff_timer_start = None

        # Hardcode Gazebo Spawns to facilitate Local-to-Global translation
        self.gz_spawns = {
            1: {'x': -7.0, 'y': 5.0},
            2: {'x': -7.0, 'y': 4.0},
            3: {'x': -7.0, 'y': 6.0},
        }

        # 6 fixed locations in front of the hexagon walls (Gazebo ENU Coordinates)
        self.wall_waypoints = [
            {'x':  3.50, 'y':  0.00, 'gz_yaw':  0.000},
            {'x':  1.75, 'y':  3.03, 'gz_yaw':  1.047},
            {'x': -1.75, 'y':  3.03, 'gz_yaw':  2.094},
            {'x': -3.50, 'y':  0.00, 'gz_yaw':  3.142},
            {'x': -1.75, 'y': -3.03, 'gz_yaw': -2.094},
            {'x':  1.75, 'y': -3.03, 'gz_yaw': -1.047},
        ]
        self.current_wp_idx = 0

        # Drone 1 Targets in PX4 Local NED space
        self.d1_target_x = 0.0
        self.d1_target_y = 0.0
        self.d1_target_yaw = 0.0

        self.setpoint_pubs = {}
        self.last_pose = {}
        for i in range(1, self.drone_count + 1):
            self.setpoint_pubs[i] = self.create_publisher(
                PoseStamped, f'/drone{i}/setpoint_position', 10
            )
            self.create_subscription(
                PoseStamped, f'/drone{i}/pose', lambda msg, idx=i: self._pose_cb(msg, idx), 10
            )

        self.create_subscription(String, '/qr_decoded', self._qr_cb, 10)

        self.state = 'TAKEOFF'
        self.state_started = self.get_clock().now()
        self.last_qr_payload = ''
        self.qr_seen = False

        period = 1.0 / self.publish_rate_hz if self.publish_rate_hz > 0.0 else 0.05
        self.timer = self.create_timer(period, self._tick)
        self.get_logger().info('Mission sequencer started! Executing 6-wall scan.')

    # Coordinate mapping: PX4 Local NED <-> Gazebo Global ENU
    def _local_to_global(self, idx: int, px4_x: float, px4_y: float):
        gz_x = px4_y + self.gz_spawns[idx]['x']
        gz_y = px4_x + self.gz_spawns[idx]['y']
        return gz_x, gz_y

    def _global_to_local(self, idx: int, gz_x: float, gz_y: float):
        px4_x = gz_y - self.gz_spawns[idx]['y']
        px4_y = gz_x - self.gz_spawns[idx]['x']
        return px4_x, px4_y

    def _pose_cb(self, msg: PoseStamped, idx: int):
        self.last_pose[idx] = msg

    def _qr_cb(self, msg: String):
        payload = msg.data.strip()
        if payload:
            self.qr_seen = True
            self.last_qr_payload = payload

    def _elapsed_s(self) -> float:
        return (self.get_clock().now() - self.state_started).nanoseconds / 1e9

    def _publish_setpoint(self, idx: int, px4_x: float, px4_y: float, px4_z: float, px4_yaw: float):
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'
        msg.pose.position.x = float(px4_x)
        msg.pose.position.y = float(px4_y)
        msg.pose.position.z = float(px4_z)
        msg.pose.orientation = yaw_to_quaternion(px4_yaw)
        self.setpoint_pubs[idx].publish(msg)

    def _drone_near_target(self, idx: int, x: float, y: float, z: float) -> bool:
        pose = self.last_pose.get(idx)
        if pose is None:
            return False
        dx = pose.pose.position.x - x
        dy = pose.pose.position.y - y
        dz = pose.pose.position.z - z
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        return dist <= self.transit_tolerance_m

    def _set_state(self, new_state: str):
        if new_state != self.state:
            self.state = new_state
            self.state_started = self.get_clock().now()
            self.get_logger().info(f'Mission state -> {new_state}')

    def _update_wall_targets(self):
        wp = self.wall_waypoints[self.current_wp_idx]
        gz_x = wp['x']
        gz_y = wp['y']
        gz_yaw = wp['gz_yaw']

        px4_x, px4_y = self._global_to_local(1, gz_x, gz_y)
        self.d1_target_x = px4_x
        self.d1_target_y = px4_y
        self.d1_target_yaw = (math.pi / 2.0) - gz_yaw

    def _tick(self):
        if self.state == 'TAKEOFF':
            all_ready = True
            for i in range(1, self.drone_count + 1):
                self._publish_setpoint(i, 0.0, 0.0, self.takeoff_z, 0.0)
                pose = self.last_pose.get(i)
                if pose is None or abs(pose.pose.position.z - self.takeoff_z) > self.transit_tolerance_m:
                    all_ready = False

            if all_ready:
                if self.takeoff_timer_start is None:
                    self.takeoff_timer_start = self._elapsed_s()
                elif self._elapsed_s() - self.takeoff_timer_start >= self.takeoff_hold_s:
                    self.current_wp_idx = 0
                    self._update_wall_targets()
                    self._set_state('TRANSIT_TO_WALL')
            else:
                self.takeoff_timer_start = None
            return

        elif self.state == 'TRANSIT_TO_WALL':
            # It flies across the map at takeoff_z. Once it spans the XY location, it drops.
            if self._drone_near_target(1, self.d1_target_x, self.d1_target_y, self.takeoff_z):
                self._set_state('HOLD_AND_SCAN')

        elif self.state == 'HOLD_AND_SCAN':
            if self.qr_seen:
                self.get_logger().info(f'QR dynamically decoded: {self.last_qr_payload}')
                self._set_state('MISSION_DONE')
            elif self._elapsed_s() >= self.target_hold_s:
                self.get_logger().warn(f'QR not decoded at wall {self.current_wp_idx + 1}. Transitioning.')
                self.current_wp_idx += 1
                if self.current_wp_idx < len(self.wall_waypoints):
                    self._update_wall_targets()
                    self._set_state('TRANSIT_TO_WALL')
                else:
                    self.get_logger().error('All 6 walls fully scanned but no decoded QR payload found.')
                    self._set_state('MISSION_DONE')

        if self.state in ['HOLD_AND_SCAN', 'MISSION_DONE']:
            z_target = self.wall_z
        else:
            z_target = self.takeoff_z

        self._publish_setpoint(1, self.d1_target_x, self.d1_target_y, z_target, self.d1_target_yaw)

        # Retrieve actual Drone 1 telemetry, map to Gazebo, calculate offsets, map back to Local PX4
        d1_actual = self.last_pose.get(1)
        if d1_actual:
            a_px4_x = d1_actual.pose.position.x
            a_px4_y = d1_actual.pose.position.y
        else:
            a_px4_x = self.d1_target_x
            a_px4_y = self.d1_target_y

        gz_x, gz_y = self._local_to_global(1, a_px4_x, a_px4_y)
        
        # Follower V-formation offsets calculated cleanly in Gazebo metrics
        for i in range(2, self.drone_count + 1):
            if i == 2:
                # Right rear in Gazebo (relative to +X wall target)
                t_gz_x = gz_x - 2.0 * math.cos((math.pi / 2.0) - self.d1_target_yaw) + 2.0 * math.sin((math.pi / 2.0) - self.d1_target_yaw)
                t_gz_y = gz_y - 2.0 * math.sin((math.pi / 2.0) - self.d1_target_yaw) - 2.0 * math.cos((math.pi / 2.0) - self.d1_target_yaw)
            elif i == 3:
                # Left rear in Gazebo
                t_gz_x = gz_x - 2.0 * math.cos((math.pi / 2.0) - self.d1_target_yaw) - 2.0 * math.sin((math.pi / 2.0) - self.d1_target_yaw)
                t_gz_y = gz_y - 2.0 * math.sin((math.pi / 2.0) - self.d1_target_yaw) + 2.0 * math.cos((math.pi / 2.0) - self.d1_target_yaw)
            else:
                t_gz_x = gz_x
                t_gz_y = gz_y

            t_px4_x, t_px4_y = self._global_to_local(i, t_gz_x, t_gz_y)
            self._publish_setpoint(i, t_px4_x, t_px4_y, z_target, self.d1_target_yaw)


def main():
    rclpy.init()
    node = MissionSequencer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
