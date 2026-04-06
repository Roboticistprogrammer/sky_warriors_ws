#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from px4_msgs.msg import VehicleLocalPosition
from geometry_msgs.msg import PoseStamped

class PX4PoseBridge(Node):
    def __init__(self):
        super().__init__('px4_pose_bridge')
        
        # Parameters
        self.declare_parameter('drone_count', 3)
        if not self.has_parameter('use_sim_time'):
            self.declare_parameter('use_sim_time', False)
        drone_count = self.get_parameter('drone_count').value
        
        self.pose_publishers = {}
        qos_profile = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
        )

        for i in range(drone_count):
            drone_name = f"drone{i+1}"
            
            # Always use fully namespaced topics for multi-vehicle simulation
            px4_topic = f'/px4_{i + 1}/fmu/out/vehicle_local_position_v1'
            
            # Subscribe to PX4 position
            self.create_subscription(
                VehicleLocalPosition,
                px4_topic,
                lambda msg, name=drone_name: self.position_callback(msg, name),
                qos_profile)

            self.get_logger().info(f'Subscribed to {px4_topic} for {drone_name}')
            
            # Publish as PoseStamped
            self.pose_publishers[drone_name] = self.create_publisher(
                PoseStamped,
                f'/{drone_name}/pose',
                10)
        
        self.get_logger().info(f'PX4 Pose Bridge started for {drone_count} drones')
    
    def position_callback(self, msg, drone_name):
        pose_msg = PoseStamped()
        pose_msg.header.stamp = self.get_clock().now().to_msg()
        pose_msg.header.frame_id = 'map'
        
        # PX4 uses NED (North-East-Down), convert if needed
        pose_msg.pose.position.x = msg.x
        pose_msg.pose.position.y = msg.y
        pose_msg.pose.position.z = msg.z
        
        self.pose_publishers[drone_name].publish(pose_msg)

def main():
    rclpy.init()
    node = PX4PoseBridge()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
