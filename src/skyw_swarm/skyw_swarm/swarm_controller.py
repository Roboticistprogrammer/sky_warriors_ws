#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from geometry_msgs.msg import PoseStamped
from formation_math import FORMATION_BUILDERS


class SwarmController(Node):

    def __init__(self):
        super().__init__('swarm_controller')

        self.declare_parameter('formation_type', 'line')
        self.declare_parameter('spacing', 2.0)
        self.declare_parameter('altitude', 3.0)
        self.declare_parameter('rotation', 0.0)
        self.declare_parameter('drone_count', 3)
        self.declare_parameter('publish_rate_hz', 20.0)
        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', False)

        self.formation_type = self.get_parameter('formation_type').value
        self.spacing = float(self.get_parameter('spacing').value)
        self.altitude = float(self.get_parameter('altitude').value)
        self.rotation = float(self.get_parameter('rotation').value)
        self.drone_count = int(self.get_parameter('drone_count').value)
        self.publish_rate_hz = float(self.get_parameter('publish_rate_hz').value)

        self.drone_positions = {}
        self.position_pubs = {}

        self.add_on_set_parameters_callback(self._on_param_change)

        for i in range(self.drone_count):
            name = f"drone{i + 1}"
            self.create_subscription(
                PoseStamped,
                f"/{name}/pose",
                lambda msg, n=name: self._pose_callback(msg, n),
                10,
            )
            self.position_pubs[name] = self.create_publisher(
                PoseStamped,
                f"/{name}/setpoint_position",
                10,
            )

        period = 1.0 / self.publish_rate_hz if self.publish_rate_hz > 0 else 0.05
        self.timer = self.create_timer(period, self._publish_targets)

        self.get_logger().info('Swarm controller ready.')

    def _on_param_change(self, params):
        for param in params:
            if param.name == 'drone_count':
                return SetParametersResult(
                    successful=False,
                    reason='drone_count change requires restart',
                )

        for param in params:
            if param.name == 'formation_type':
                self.formation_type = str(param.value)
            elif param.name == 'spacing':
                self.spacing = float(param.value)
            elif param.name == 'altitude':
                self.altitude = float(param.value)
            elif param.name == 'rotation':
                self.rotation = float(param.value)
            elif param.name == 'publish_rate_hz':
                self.publish_rate_hz = float(param.value)
                period = 1.0 / self.publish_rate_hz if self.publish_rate_hz > 0 else 0.05
                self.timer.cancel()
                self.timer = self.create_timer(period, self._publish_targets)

        return SetParametersResult(successful=True)

    def _pose_callback(self, msg, name):
        self.drone_positions[name] = [
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z,
        ]

    def _publish_targets(self):
        formation_type = self.formation_type
        drone_names = list(self.position_pubs.keys())

        if formation_type == 'hold':
            targets = []
            for name in drone_names:
                if name not in self.drone_positions:
                    return
                targets.append(self.drone_positions[name])
        else:
            if formation_type not in FORMATION_BUILDERS:
                self.get_logger().warn(f"Unknown formation_type: {formation_type}")
                return

            leader = self.drone_positions.get('drone1', [0.0, 0.0, self.altitude])
            targets = FORMATION_BUILDERS[formation_type](
                self.spacing,
                self.drone_count,
                leader,
                self.altitude,
                self.rotation,
            )

        stamp = self.get_clock().now().to_msg()
        for i, name in enumerate(drone_names):
            msg = PoseStamped()
            msg.header.stamp = stamp
            msg.header.frame_id = 'map'
            msg.pose.position.x = float(targets[i][0])
            msg.pose.position.y = float(targets[i][1])
            msg.pose.position.z = float(targets[i][2])
            self.position_pubs[name].publish(msg)


def main():
    rclpy.init()
    node = SwarmController()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
