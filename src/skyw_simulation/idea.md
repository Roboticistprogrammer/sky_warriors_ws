Here are the best practices for developing a robust swarm package, focusing on resolving backend and QoS conflicts.
1. Middleware Backend Strategy
The "backend" usually refers to either the transport layer or the ROS 2 Middleware (RMW) implementation.
Standard: uXRCE-DDS (Micro-XRCE-DDS)
Why: It replaces the old Fast-RTPS bridge. It allows the flight controller (client) to publish specific topics to the DDS world via an Agent running on your companion computer.
Backend Implementation (RMW): Stick to rmw_fastrtps_cpp (Fast DDS) for your ROS 2 nodes. Since the Micro-XRCE-DDS Agent is developed by eProsima (same as Fast DDS), this minimizes compatibility issues regarding data serialization and discovery.
Tip: If you must use CycloneDDS, ensure you are not facing "Type Hash" conflicts (common in ROS 2 Humble/Iron when mixing bridges).
Transport: For swarms, UDP is preferred over Serial to handle higher throughput, provided you have a stable WiFi/network. 
2. QoS Streaming: The "Golden Rule"
PX4 does not use standard ROS 2 default QoS settings. If your package uses default subscribers, you will receive no data (the "incompatible QoS" error). 
The PX4 QoS Profile:
Most high-frequency telemetry from PX4 (e.g., VehicleOdometry, SensorCombined) is published with:
Reliability: BEST_EFFORT (Not Reliable)
Durability: TRANSIENT_LOCAL (or VOLATILE depending on the topic)
History: KEEP_LAST (Depth: 1) 
Best Practice Code (Python example):
Do not use qos_profile_sensor_data blindly. Explicitly define the profile to match PX4's publisher. 
python
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy

# Matches PX4 publisher settings for most topics
px4_qos_profile = QoSProfile(
    reliability=ReliabilityPolicy.BEST_EFFORT,
    durability=DurabilityPolicy.TRANSIENT_LOCAL,
    history=HistoryPolicy.KEEP_LAST,
    depth=1
)

self.subscription = self.create_subscription(
    VehicleOdometry,
    '/fmu/out/vehicle_odometry',
    self.listener_callback,
    px4_qos_profile  # <--- CRITICAL
)
3. Swarm Namespace Management
In a swarm, uORB topics must be namespaced to avoid collision (e.g., Drone 1 overwriting Drone 2's odometry).
PX4 Side (Client): Use the parameter UXRCE_DDS_NS_IDX or UXRCE_DDS_KEY.
Setting UXRCE_DDS_NS_IDX to 1 automatically prefixes topics with /px4_1/ (depending on your firmware version logic) or allows you to map IDs to namespaces.
ROS 2 Side (Agent):
Simulation: You generally run one Agent per vehicle on different UDP ports.
Real Hardware: Each drone runs its own Agent locally on its companion computer. The DDS network handles the aggregation. You must ensure unique ROS_DOMAIN_ID or proper namespacing so your ground station sees /drone1/fmu/... and /drone2/fmu/.... 
4. Bandwidth Optimization (The dds_topics.yaml file) 
Swarming kills WiFi bandwidth. A common mistake is streaming all uORB topics. 
Solution: Modify the dds_topics.yaml file in the PX4 source tree (src/modules/uxrce_dds_client/dds_topics.yaml) before building the firmware.
Action: Comment out high-bandwidth topics you don't need (e.g., debug vectors, raw estimator states) and keep only essential swarm topics like:
VehicleLocalPosition (or VehicleOdometry)
VehicleStatus
VehicleCommand (for sending inputs)
OffboardControlMode 
5. Summary Checklist for Your Package
Launch File: Create a ROS 2 launch file that accepts an ns (namespace) argument and pushes it to all nodes.
Dependency: Depend on px4_msgs (ensure it matches your PX4 firmware version exactly).
Check QoS: Verify every subscriber in your code uses ReliabilityPolicy.BEST_EFFORT.
Network: If real-world, check your multicast support on the router. DDS relies heavily on multicast for discovery. If multicast is blocked, nodes won't find each other. 
Debugging Command:
Use the ROS 2 CLI to check QoS compatibility if a topic is silent: 
bash
ros2 topic info /fmu/out/vehicle_odometry --verbose
Look for "Offered QoS" (Publisher) vs "Requested QoS" (Subscriber). If they differ in Reliability or Durability, they will not connect. 