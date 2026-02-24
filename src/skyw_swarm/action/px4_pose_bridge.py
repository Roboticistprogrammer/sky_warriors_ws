#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from px4_msgs.msg import VehicleLocalPosition
from geometry_msgs.msg import PoseStamped

class PX4PoseBridge(Node):
    def __init__(self):
        super().__init__('px4_pose_bridge')
        
        # Parameters
        self.declare_parameter('drone_count', 2)
        drone_count = self.get_parameter('drone_count').value
        
        self.publishers = {}
        
        for i in range(drone_count):
            drone_name = f"drone{i+1}"
            
            # For first drone (no namespace)
            if i == 0:
                px4_topic = '/fmu/out/vehicle_local_position_v1'
            else:
                # For additional drones (px4_1, px4_2, etc.)
                px4_topic = f'/px4_{i}/fmu/out/vehicle_local_position_v1'
            
            # Subscribe to PX4 position
            self.create_subscription(
                VehicleLocalPosition,
                px4_topic,
                lambda msg, name=drone_name: self.position_callback(msg, name),
                10)
            
            # Publish as PoseStamped
            self.publishers[drone_name] = self.create_publisher(
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
        
        self.publishers[drone_name].publish(pose_msg)

def main():
    rclpy.init()
    node = PX4PoseBridge()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
