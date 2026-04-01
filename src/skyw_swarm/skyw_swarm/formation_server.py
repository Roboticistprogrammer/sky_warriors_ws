#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from skyw_swarm.action import SetFormation
from geometry_msgs.msg import PoseStamped
from formation_math import FORMATION_BUILDERS


class FormationServer(Node):

    def __init__(self):
        super().__init__('formation_server')
        
        self.get_logger().info('Formation Server starting...')

        self._action_server = ActionServer(
            self,
            SetFormation,
            'set_formation',
            self.execute_callback)

        self.drone_positions = {}
        self.position_pubs = {}

        self.declare_parameter("drone_count", 3)
        self.declare_parameter("default_formation", "arrow_head")
        self.declare_parameter("default_spacing", 2.0)
        self.declare_parameter("default_altitude", 3.0)
        self.declare_parameter("default_rotation", 0.0)
        self.declare_parameter("publish_rate_hz", 20.0)
        self.declare_parameter("publish_steps", 200)
        self.declare_parameter("wait_for_pose_timeout_s", 5.0)
        if not self.has_parameter("use_sim_time"):
            self.declare_parameter("use_sim_time", False)

        drone_count = self.get_parameter("drone_count").value
        
        self.get_logger().info(f'Waiting for {drone_count} drones...')

        for i in range(drone_count):
            name = f"drone{i+1}"

            self.create_subscription(
                PoseStamped,
                f"/{name}/pose",
                lambda msg, n=name: self.pose_callback(msg, n),
                10)

            self.position_pubs[name] = self.create_publisher(
                PoseStamped,
                f"/{name}/setpoint_position",
                10)

    def pose_callback(self, msg, name):
        self.drone_positions[name] = [
            msg.pose.position.x,
            msg.pose.position.y,
            msg.pose.position.z
        ]

    async def execute_callback(self, goal_handle):

        self.get_logger().info("Formation goal received")

        formation_type = goal_handle.request.formation_type
        spacing = goal_handle.request.spacing
        altitude = goal_handle.request.altitude
        rotation = goal_handle.request.rotation
        drone_count = goal_handle.request.drone_count

        if not formation_type:
            formation_type = self.get_parameter("default_formation").value
        if spacing <= 0.0:
            spacing = self.get_parameter("default_spacing").value
        if altitude <= 0.0:
            altitude = self.get_parameter("default_altitude").value
        if drone_count == 0:
            drone_count = self.get_parameter("drone_count").value

        leader_name = "drone1"

        timeout_s = float(self.get_parameter("wait_for_pose_timeout_s").value)
        start_time = self.get_clock().now()
        while leader_name not in self.drone_positions:
            if (self.get_clock().now() - start_time).nanoseconds / 1e9 > timeout_s:
                self.get_logger().error("Timed out waiting for leader pose")
                goal_handle.abort()
                return SetFormation.Result(success=False)
            rclpy.spin_once(self, timeout_sec=0.05)

        center = self.drone_positions[leader_name]

        if formation_type not in FORMATION_BUILDERS:
            goal_handle.abort()
            return SetFormation.Result(success=False)

        targets = FORMATION_BUILDERS[formation_type](
            spacing,
            drone_count,
            center,
            altitude,
            rotation,
        )

        drone_names = list(self.position_pubs.keys())

        publish_steps = int(self.get_parameter("publish_steps").value)
        publish_rate_hz = float(self.get_parameter("publish_rate_hz").value)
        publish_period = 1.0 / publish_rate_hz if publish_rate_hz > 0 else 0.05

        for step in range(publish_steps):

            for i, name in enumerate(drone_names):
                msg = PoseStamped()
                msg.pose.position.x = float(targets[i][0])
                msg.pose.position.y = float(targets[i][1])
                msg.pose.position.z = float(targets[i][2])
                self.position_pubs[name].publish(msg)

            feedback = SetFormation.Feedback()
            feedback.progress = (step + 1) / max(publish_steps, 1) * 100.0
            goal_handle.publish_feedback(feedback)

            rclpy.spin_once(self, timeout_sec=publish_period)

        goal_handle.succeed()
        return SetFormation.Result(success=True)


def main():
    rclpy.init()
    node = FormationServer()
    node.get_logger().info('Formation Server ready! Waiting for action goals...')
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
