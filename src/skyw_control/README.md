# Sky Warrior Control Package

This package provides scalable multi-drone control algorithms for testing and deploying control laws on UAV fleets. The default controller implements a leader-follower formation control approach based on the paper:

**Reference:** [Distributed leader-follower formation control for multiple quadrotors with weighted topology](https://hal.science/hal-01180491/document) by Zhicheng Hou and Isabelle Fantoni.

## Running the Controller

```bash
source ~/sky_warrior_ws/install/setup.bash
ros2 launch skyw_control <launch_file>
```
## Configuration

### Configuration Files

The following configuration files control the swarm behavior:

- **`config/swarm_config.json`** - Swarm setup and drone parameters
- **`config/control_config.json`** - Controller parameters and modes
- **`config/gains.yaml`** - PID controller gains
- **`config/Trajectories/`** - Predefined waypoint trajectories

### Modifying Configuration

Edit these configuration files on your host machine and rebuild the package:

```bash
colcon build --packages-select skyw_control
source install/setup.bash
```

## Gazebo Garden vs Classic

This setup uses **Gazebo Garden** (new generation):

| Feature | Gazebo Classic | Gazebo Garden |
|---------|---------------|---------------|
| Command | `gazebo` | `gz sim` |
| Performance | Good | Better |
| Physics | ODE | Multiple engines |
| Sensors | Limited | Enhanced |

**PX4 Models for Garden:**
- `x500` - Quadcopter (default)
- `x500_depth` - With depth camera
- `rc_cessna` - Fixed-wing
- `standard_vtol` - VTOL aircraft
