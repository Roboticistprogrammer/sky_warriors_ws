#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from skyw_swarm.action import SetFormation

class FormationClient(Node):

    def __init__(self):
        super().__init__('formation_client')
        self._client = ActionClient(self, SetFormation, 'set_formation')

    def send_goal(self, formation_type='v', spacing=2.0, altitude=3.0, rotation=0.0, drone_count=2):
        self.get_logger().info('Waiting for action server...')
        self._client.wait_for_server()
        
        goal_msg = SetFormation.Goal()
        goal_msg.formation_type = formation_type
        goal_msg.spacing = spacing
        goal_msg.altitude = altitude
        goal_msg.rotation = rotation
        goal_msg.drone_count = drone_count

        self.get_logger().info(f'Sending goal: {formation_type} formation with {drone_count} drones')
        
        self._send_goal_future = self._client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback)
        
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted! Executing...')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        if result.success:
            self.get_logger().info('Formation completed successfully!')
        else:
            self.get_logger().info('Formation failed!')
        rclpy.shutdown()

    def feedback_callback(self, feedback_msg):
        progress = feedback_msg.feedback.progress
        self.get_logger().info(f'Progress: {progress:.1f}%')


def main():
    rclpy.init()
    node = FormationClient()
    node.send_goal()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
