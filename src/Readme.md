# Sky Warrior Packages

This directory contains ROS 2 packages for the Sky Warrior multi-drone system. Each folder is a dedicated ROS 2 package for a specific task.

## Package Overview

- **skyw_simulation** - Gazebo simulation environment for spawning drones
- **skyw_control** - Multi-drone control algorithms and formation control
- **skyw_swarm** - Swarm behavior coordination
- **skyw_detection** - QR code detection and decoding
- **skyw_bringup** - Launch configurations
- **skyw_interfaces** - Custom ROS 2 messages and services
- **skyw_utils** - Utility functions and tools

## Quick Start
git clone

git clone https://github.com/Roboticistprogrammer/sky_warriors_ws.git && cd sky_warriors_ws
vcs import src/thirdparty < dependencies.repos
colcon build px4_msgs px4_ros_com


To get started with the simulation:

1. Start the sim stack manually with `skyw_simulation`:
cd /skyw_warriors_ws
./src/skyw_simulation/startup.sh

2. Start the mission-control launch in another terminal:
cd /skyw_warriors_ws
source install/setup.bash
ros2 launch skyw_control launch_simulation.py

3. Review [src/Sim-Scenario.md](/home/pouya/Projects/sky_warriors_ws/src/Sim-Scenario.md) for the expected phase flow and validation checklist.

## Development Status

**Note:** Several packages (`skyw_control`, `skyw_swarm`, `skyw_detection`) are under active development. Each team should:

1. Fork the repository
2. Focus on their assigned package
3. Create pull requests with implemented features
4. Document any issues or blockers

## Contributing

When working on a specific package, ensure you test your changes in the simulation environment before submitting pull requests. 
