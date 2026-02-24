#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from skyw_swarm.action import SetFormation
from geometry_msgs.msg import PoseStamped
import numpy as np
import math

def rotate_2d(points, angle_deg):
    angle = math.radians(angle_deg)
    R = np.array([
        [math.cos(angle), -math.sin(angle)],
        [math.sin(angle),  math.cos(angle)]
    ])
    return (R @ points.T).T

def line_formation(spacing, drone_count, center, altitude, rotation):
    """Create a straight horizontal line centered at leader"""
    desired = []
    offset = (drone_count - 1) / 2.0
    for i in range(drone_count):
        x = (i - offset) * spacing
        y = 0
        desired.append([x, y])
    desired = np.array(desired)
    desired = rotate_2d(desired, rotation)
    final = []
    for i in range(drone_count):
        final.append([
            center[0] + desired[i][0],
            center[1] + desired[i][1],
            altitude
        ])
    return np.array(final)

def v_formation(spacing, drone_count, center, altitude, rotation):
    """Leader at front, others distributed equally on both wings"""
    desired = []
    desired.append([0, 0])  # leader
    wing_index = 1
    side = -1
    for i in range(1, drone_count):
        x = wing_index * spacing
        y = side * wing_index * spacing
        desired.append([x, y])
        side *= -1
        if side == -1:
            wing_index += 1
    desired = np.array(desired)
    desired = rotate_2d(desired, rotation)
    final = []
    for i in range(drone_count):
        final.append([
            center[0] + desired[i][0],
            center[1] + desired[i][1],
            altitude
        ])
    return np.array(final)


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

        leader_name = "drone1"

        while leader_name not in self.drone_positions:
            pass

        center = self.drone_positions[leader_name]

        if formation_type == "line":
            targets = line_formation(spacing, drone_count, center, altitude, rotation)
        elif formation_type == "v":
            targets = v_formation(spacing, drone_count, center, altitude, rotation)
        else:
            goal_handle.abort()
            return SetFormation.Result(success=False)

        drone_names = list(self.position_pubs.keys())

        for step in range(200):

            for i, name in enumerate(drone_names):
                msg = PoseStamped()
                msg.pose.position.x = float(targets[i][0])
                msg.pose.position.y = float(targets[i][1])
                msg.pose.position.z = float(targets[i][2])
                self.position_pubs[name].publish(msg)

            feedback = SetFormation.Feedback()
            feedback.progress = step / 2.0
            goal_handle.publish_feedback(feedback)

            rclpy.spin_once(self, timeout_sec=0.05)

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
