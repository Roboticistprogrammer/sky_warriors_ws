# Sky Warrior Packages

This directory contains ROS 2 packages for the Sky Warrior multi-drone system. Each folder is a dedicated ROS 2 package for a specific task.

## Package Overview

- **skyw_simulation** - Gazebo simulation environment for spawning drones
- **skyw_control** - Multi-drone control algorithms and formation control
- **skyw_swarm** - Swarm behavior coordination
- **skyw_detection** - QR code detection and decoding
- **skyw_comm** - Communication protocols
- **skyw_bringup** - Launch configurations
- **skyw_interfaces** - Custom ROS 2 messages and services
- **skyw_utils** - Utility functions and tools

## Quick Start

To get started with the simulation:

1. From `src/`, run `./launch_gz_px4_sitl.sh 3 x500` to start Gazebo Harmonic + PX4 SITL and spawn 3 drones
2. Run the Micro-XRCE-DDS Agent to connect ROS 2 and QGroundControl to the UAVs
3. Launch the desired control or detection package

## Development Status

**Note:** Several packages (`skyw_control`, `skyw_swarm`, `skyw_detection`) are under active development. Each team should:

1. Fork the repository
2. Focus on their assigned package
3. Create pull requests with implemented features
4. Document any issues or blockers

## Contributing

When working on a specific package, ensure you test your changes in the simulation environment before submitting pull requests. 
