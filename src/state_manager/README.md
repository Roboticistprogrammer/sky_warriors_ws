# state_manager

A ROS2 package for centralized swarm state management using a finite state machine (FSM).

## Purpose
- Manages swarm states (e.g., FORMATION, DETACHING, WAITING, RECONFIGURING, IDLE).
- Listens to QR detection, manual commands, and UAV status topics.
- Publishes commands to control UAVs (detach, formation, etc.).
- Can operate independently of CBBA or any other allocation logic.

## Key Features
- Modular and extensible FSM logic.
- ROS2 topic-based communication for easy integration.
- Easily add new states, triggers, and outputs as needed.

## Structure
- `state_manager_node.py`: Main FSM node implementation.
- `state_manager_demo_node.py`: Simple detachment scenario publisher for testing.
- `launch/`: Launch files for easy startup.
- `params/`: YAML parameter files.
- `resource/`: Package resource files.
- `README.md`: This file.

## Example Topics
- Input: `/qr_decoded`, `/manual_command`, `/uav_status`
- Output: `/swarm/state_change`, `/swarm/detach_command`, `/swarm/formation_command`
- Service: `/swarm/request_detach`

## Recommended Launch (ROS 2 Humble)
- `state_manager.launch.py`: Starts the FSM node with parameters.
- `state_manager_detach_demo.launch.py`: Starts the FSM and a demo scenario node.

### Example Usage
```bash
ros2 launch state_manager state_manager.launch.py
```

```bash
ros2 launch state_manager state_manager_detach_demo.launch.py trigger_mode:=manual
```

## Simple Detachment Scenario
1. Use `skyw_bringup/startup.sh` to spawn 3 UAVs.
2. Launch the state manager with the demo scenario.
3. The demo node publishes a detach trigger, then a detached status, then a formation command.

You can observe the FSM outputs with:
```bash
ros2 topic echo /swarm/state_change
ros2 topic echo /swarm/detach_command
ros2 topic echo /swarm/formation_command
```

## How to Extend
- Add new subscriptions for more triggers (e.g., emergencies).
- Add new publishers for new commands (e.g., land, return home).
- Implement more complex state logic as needed.

---

This package was created based on a design discussion to provide a flexible, standalone FSM for UAV swarm management, with or without CBBA integration.