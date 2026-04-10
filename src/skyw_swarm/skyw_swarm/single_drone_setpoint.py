#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped


class SingleDroneSetpoint(Node):
    def __init__(self):
        super().__init__('single_drone_setpoint')

        self.declare_parameter('drone_id', 1)
        self.declare_parameter('drone_ns_prefix', '/drone')
        self.declare_parameter('target_x', 0.0)
        self.declare_parameter('target_y', 0.0)
        self.declare_parameter('target_z', -2.5)
        self.declare_parameter('target_yaw', 0.0)
        self.declare_parameter('rate_hz', 20.0)
        self.declare_parameter('frame_id', 'map')
        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', False)

        drone_id = int(self.get_parameter('drone_id').value)
        ns_prefix = str(self.get_parameter('drone_ns_prefix').value).rstrip('/')
        topic = f"{ns_prefix}{drone_id}/setpoint_position"

        self.target_x = float(self.get_parameter('target_x').value)
        self.target_y = float(self.get_parameter('target_y').value)
        self.target_z = float(self.get_parameter('target_z').value)
        self.target_yaw = float(self.get_parameter('target_yaw').value)
        self.frame_id = str(self.get_parameter('frame_id').value)

        self.publisher = self.create_publisher(PoseStamped, topic, 10)

        rate_hz = float(self.get_parameter('rate_hz').value)
        period = 1.0 / rate_hz if rate_hz > 0 else 0.05
        self.timer = self.create_timer(period, self._publish_setpoint)

        self.get_logger().info(
            f"Publishing setpoints to {topic} at {rate_hz:.1f} Hz"
        )

    def _publish_setpoint(self):
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id
        msg.pose.position.x = self.target_x
        msg.pose.position.y = self.target_y
        msg.pose.position.z = self.target_z

        yaw = self.target_yaw
        msg.pose.orientation.x = 0.0
        msg.pose.orientation.y = 0.0
        msg.pose.orientation.z = math.sin(yaw * 0.5)
        msg.pose.orientation.w = math.cos(yaw * 0.5)

        self.publisher.publish(msg)


def main():
    rclpy.init()
    node = SingleDroneSetpoint()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
