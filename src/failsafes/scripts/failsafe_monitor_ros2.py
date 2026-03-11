#!/usr/bin/env python3
"""
ROS 2 based failsafe testing
Uses ROS 2 topics to monitor and inject failures
"""

import rclpy
from rclpy.node import Node
from px4_msgs.msg import VehicleStatus, VehicleLocalPosition
import time


class FailsafeMonitor(Node):
    def __init__(self):
        super().__init__('failsafe_monitor')
        
        # Subscribers
        self.status_sub = self.create_subscription(
            VehicleStatus,
            '/fmu/out/vehicle_status',
            self.status_callback,
            10
        )
        
        self.position_sub = self.create_subscription(
            VehicleLocalPosition,
            '/fmu/out/vehicle_local_position',
            self.position_callback,
            10
        )
        
        self.current_nav_state = None
        self.current_arming_state = None
        self.current_failsafe = False
        
        self.get_logger().info("Failsafe Monitor started")
        
    def status_callback(self, msg):
        """Monitor vehicle status for failsafe activations"""
        
        # Check if nav state changed
        if self.current_nav_state != msg.nav_state:
            self.get_logger().info(f"Nav State changed: {self.current_nav_state} -> {msg.nav_state}")
            self.current_nav_state = msg.nav_state
            
            # Decode nav state (simplified)
            nav_state_names = {
                0: "MANUAL",
                1: "ALTCTL",
                2: "POSCTL",
                3: "AUTO_MISSION",
                4: "AUTO_LOITER",
                5: "AUTO_RTL",
                6: "AUTO_LANDENGFAIL",
                17: "OFFBOARD",
            }
            
            state_name = nav_state_names.get(msg.nav_state, f"UNKNOWN({msg.nav_state})")
            self.get_logger().info(f"  -> {state_name}")
            
            # Detect RTL activation (possible failsafe)
            if msg.nav_state == 5:  # AUTO_RTL
                self.get_logger().warn("⚠️  RTL ACTIVATED - Possible Failsafe!")
                
        # Check arming state
        if self.current_arming_state != msg.arming_state:
            self.get_logger().info(f"Arming State: {msg.arming_state}")
            self.current_arming_state = msg.arming_state
            
        # Check failsafe flag
        if msg.failsafe != self.current_failsafe:
            self.current_failsafe = msg.failsafe
            if msg.failsafe:
                self.get_logger().error("🚨 FAILSAFE ACTIVATED! 🚨")
            else:
                self.get_logger().info("✅ Failsafe cleared")
                
    def position_callback(self, msg):
        """Monitor position"""
        # Could log position changes, geofence breaches, etc.
        pass


def main(args=None):
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║         Failsafe Monitor (ROS 2)                      ║
    ║         Monitors PX4 status via ROS 2 topics          ║
    ╚════════════════════════════════════════════════════════╝
    
    This node monitors:
    - Vehicle navigation state changes
    - Arming state changes
    - Failsafe flag activations
    - RTL activations
    
    Run your failsafe tests and watch this output for state changes.
    """)
    
    rclpy.init(args=args)
    monitor = FailsafeMonitor()
    
    try:
        rclpy.spin(monitor)
    except KeyboardInterrupt:
        pass
    finally:
        monitor.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
