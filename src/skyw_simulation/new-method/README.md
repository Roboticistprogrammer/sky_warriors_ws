# New Method: Separate Gazebo and PX4 SITL

This approach runs Gazebo separately first, then spawns PX4 SITL instances that connect to the running Gazebo simulation.

Reference: https://discuss.px4.io/t/starting-px4-sitl-with-a-separate-gazebo-sim/47982/5

## ⚠️ Important for 8GB RAM Systems

If you have 8GB RAM or less, **use the optimized helper script**:
```bash
./run_on_8gb_ram.sh [NUM_VEHICLES] [VEHICLE_MODEL]

# Examples:
./run_on_8gb_ram.sh           # 1 x500 with speed factor 0.5
./run_on_8gb_ram.sh 2         # 2 x500 drones with speed factor 0.5
```

Or manually specify speed factor:
```bash
./2_spawn_px4_sitl.sh 1 x500 0.5
```

This prevents sensor detection failures and connection issues by reducing the simulation load.

## How it Works

1. **Gazebo runs standalone** with the world file (warehouse1.sdf)
2. **PX4 SITL connects** to the running Gazebo using `PX4_GZ_STANDALONE=1` and `PX4_GZ_WORLD=warehouse1`
3. PX4 looks for the Gazebo service: `/world/warehouse1/scene/info`

## Usage

### Terminal 1: Start Gazebo
```bash
cd /home/roboticistprogrammer/sky_warrior_ws/src/skyw_simulation/new-method
./1_start_gazebo.sh
```

### Terminal 2: Spawn PX4 SITL Instances

**Option A - Using px4 binary directly (recommended for multiple vehicles):**
```bash
./2_spawn_px4_sitl.sh [NUM_VEHICLES] [VEHICLE_MODEL] [SPEED_FACTOR]

# Examples:
./2_spawn_px4_sitl.sh                   # Spawn 1 x500, normal speed
./2_spawn_px4_sitl.sh 3                 # Spawn 3 x500 drones, normal speed
./2_spawn_px4_sitl.sh 2 x500 0.5        # Spawn 2 x500, 0.5 speed (for 8GB RAM)
./2_spawn_px4_sitl.sh 1 x500 0.5        # Spawn 1 x500, 0.5 speed (recommended for low RAM)
```

**Option B - Using make command (single vehicle):**
```bash
./3_spawn_using_make.sh [VEHICLE_MODEL] [INSTANCE]

# Examples:
./3_spawn_using_make.sh x500 0              # Spawn first x500
./3_spawn_using_make.sh x500_mono_cam_down 0  # Spawn x500 with camera
```

## Key Environment Variables

The scripts automatically source `gz_env.sh` which sets:
- `GZ_SIM_RESOURCE_PATH` - Where Gazebo finds models and worlds
- `GZ_SIM_SYSTEM_PLUGIN_PATH` - Where Gazebo finds plugins
- `PX4_GZ_WORLD=warehouse1` - The world name PX4 will look for

## Troubleshooting

### Sensor Missing Errors (8GB RAM Systems)

**Symptoms:**
```
WARN [health_and_arming_checks] Preflight Fail: Accel Sensor 0 missing
WARN [health_and_arming_checks] Preflight Fail: barometer 0 missing
WARN [health_and_arming_checks] Preflight Fail: Gyro Sensor 0 missing
WARN [health_and_arming_checks] Preflight Fail: Found 0 compass
INFO [commander] Connection to ground station lost
```

**Cause:** On systems with 8GB RAM or less, Gazebo loads models slowly. PX4 starts before the Gazebo model (with sensors) is fully spawned, causing sensor detection failures.

**Solutions:**
1. **Use speed factor 0.5** (less demanding on RAM):
   ```bash
   ./2_spawn_px4_sitl.sh 1 x500 0.5
   ```

2. **The script automatically detects low RAM** and uses longer wait times (10s vs 5s)

3. **Verify model spawned** - The script now checks if the model appears in Gazebo before proceeding

4. **Wait longer between spawns** - For multiple vehicles on 8GB RAM, spawn them one at a time with manual delays

**Why speed factor helps:** Setting `PX4_SIM_SPEED_FACTOR=0.5` slows the simulation to 50% real-time, which:
- Reduces computational load
- Gives Gazebo more time to initialize sensors
- Allows PX4 to properly connect to sensor data streams

### Error: "Unable to find uri[file:///.../model.sdf]"

This means `GZ_SIM_RESOURCE_PATH` is not properly set when running PX4. The scripts handle this by sourcing `gz_env.sh` before running PX4 commands.

**Solution:** Always run the scripts from this directory, or manually source the environment:
```bash
source ../gz_env.sh
```

### Error: "PX4 SITL wasn't finding the running Gazebo simulation"

This happens when `PX4_GZ_WORLD` doesn't match the actual world name. Make sure:
- The world in warehouse1.sdf is named `warehouse1` (line 3 of the SDF file)
- You set `PX4_GZ_WORLD=warehouse1` when running PX4

### libEGL warnings

The warnings about `libEGL warning: egl: failed to create dri2 screen` are usually harmless and can be ignored. They occur due to GPU/display configuration but don't affect functionality.

## Advantages of This Method

1. **Gazebo runs independently** - Can restart PX4 without restarting Gazebo
2. **Better control** - Start world first, verify it's running, then add vehicles
3. **Easier debugging** - Separate logs for Gazebo and PX4
4. **Custom worlds** - Easy to use any world name by changing `PX4_GZ_WORLD`

## Notes

- Make sure Gazebo is fully started (Terminal 1) before spawning PX4 instances (Terminal 2)
- Each vehicle gets a MAVLink port starting from 14540 (14540, 14541, 14542, ...)
- To stop: Ctrl+C in Terminal 2 kills PX4 instances, Ctrl+C in Terminal 1 kills Gazebo
