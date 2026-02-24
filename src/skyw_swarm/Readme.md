# Setup

colcon build --packages-select skyw_swarm
source install/setup.bash

# Run (3 terminals required)

## Terminal 1: PX4 Pose Bridge
ros2 run skyw_swarm px4_pose_bridge.py

## Terminal 2: Formation Server
ros2 run skyw_swarm formation_server.py --ros-args -p drone_count:=2

## Terminal 3: Formation Client
ros2 run skyw_swarm formation_client.py

# Verification
ros2 interface show skyw_swarm/action/SetFormation
ros2 node list
ros2 action list
ros2 topic list | grep pose
ros2 topic echo /drone1/pose

# Using px4 conversion node
cd ~/sky_warrior_ws
colcon build --packages-select skyw_swarm
source install/setup.bash

Terminal1
source install/setup.bash
ros2 run skyw_swarm px4_pose_bridge.py

Terminal2
source install/setup.bash
ros2 run skyw_swarm formation_server.py --ros-args -p drone_count:=2

Terminal3
source install/setup.bash
ros2 run skyw_swarm formation_client.py