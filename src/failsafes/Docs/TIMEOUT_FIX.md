# TIMEOUT Error Troubleshooting Guide

## Problem
Getting this error when trying to inject failures using MAVSDK:
```
Error during test: TIMEOUT: 'Timeout'; origin: inject(); params: (<FailureUnit.SENSOR_GPS: 4>, <FailureType.OFF: 1>, 0)
```

## Root Cause Analysis

The TIMEOUT error occurs because **PX4's MAVLink receiver is rejecting the failure injection command**. Here's why:

### Code Flow:
1. MAVSDK sends `MAV_CMD_INJECT_FAILURE` via MAVLink
2. PX4's `mavlink_receiver.cpp` receives it
3. **It checks: `if (_mavlink.failure_injection_enabled())`**
4. This checks the **`SYS_FAILURE_EN` parameter**
5. If `SYS_FAILURE_EN = 0` (disabled), command is **DENIED**
6. MAVSDK waits for acknowledgment → **TIMEOUT**

### Relevant PX4 Code:
```cpp
// In mavlink_receiver.cpp
} else if (cmd_mavlink.command == MAV_CMD_INJECT_FAILURE) {
    if (_mavlink.failure_injection_enabled()) {
        _cmd_pub.publish(vehicle_command);  // ✅ Allowed
        send_ack = false;
    } else {
        result = vehicle_command_ack_s::VEHICLE_CMD_RESULT_DENIED;  // ❌ Denied
        send_ack = true;
    }
}
```

## Solutions (In Order of Recommendation)

### Solution 1: Enable SYS_FAILURE_EN via PX4 Shell ⭐ RECOMMENDED

**Before starting PX4 SITL**, edit the params file:

```bash
# Create/edit params file
nano ~/PX4-Autopilot/build/px4_sitl_default/rootfs/0/etc/params

# Add this line:
SYS_FAILURE_EN 1

# Save and exit (Ctrl+X, Y, Enter)
```

**Then restart PX4:**
```bash
cd ~/sky_warrior_ws/src/skyw_simulation/new-method
./2_spawn_px4_sitl.sh 1
```

### Solution 2: Enable via QGroundControl

1. Connect QGC to your drone (UDP port 14540)
2. Go to: **Vehicle Setup → Parameters**
3. Search for: `SYS_FAILURE_EN`
4. Set it to: **1**
5. Click **Save** and restart PX4 SITL

### Solution 3: Enable via PX4 Console (Runtime)

While PX4 is running:
```bash
# In a new terminal
cd ~/PX4-Autopilot
./build/px4_sitl_default/bin/px4 shell -i 0

# In the PX4 shell (pxh>):
pxh> param set SYS_FAILURE_EN 1
pxh> param save
pxh> exit
```

**⚠️ Note:** Runtime changes may not persist. Better to edit params file.

### Solution 4: Use PX4's Built-in Failure Command (BYPASS MAVSDK)

This method **doesn't use MAVLink** so it bypasses the SYS_FAILURE_EN check:

```bash
# Use the provided script:
cd ~/sky_warrior_ws/src/failsafes/scripts
./test_gps_failsafe_px4cmd.sh

# Or manually:
cd ~/PX4-Autopilot
echo "failure gps off" | ./build/px4_sitl_default/bin/px4 shell -i 0
```

**✅ This always works!** Even if SYS_FAILURE_EN is disabled.

## Verification Steps

### Step 1: Check if parameter is set
```bash
cd ~/PX4-Autopilot
./build/px4_sitl_default/bin/px4 shell -i 0
pxh> param show SYS_FAILURE_EN
```

Expected output:
```
SYS_FAILURE_EN: curr: 1 default: 0
```

### Step 2: Test with updated MAVSDK script
```bash
cd ~/sky_warrior_ws/src/failsafes/scripts
python3 test_failsafe_mavsdk.py
```

The updated script will:
- Check `SYS_FAILURE_EN` automatically
- Try to enable it if disabled
- Provide clear error messages if it fails

### Step 3: Monitor PX4 output
When failure injection works, you should see in PX4 console:
```
WARN [simulator_mavlink] CMD_INJECT_FAILURE, GPS off
```

## Alternative: Use ROS 2 Method

Since you're using ROS 2, you can also inject failures via ROS 2 topics:

```bash
# Publish failure command directly to PX4
ros2 topic pub --once /fmu/in/vehicle_command px4_msgs/msg/VehicleCommand \
  "{command: 420, param1: 4.0, param2: 1.0, param3: 0.0}"
```

Where:
- `command: 420` = VEHICLE_CMD_INJECT_FAILURE
- `param1: 4.0` = FAILURE_UNIT_SENSOR_GPS
- `param2: 1.0` = FAILURE_TYPE_OFF

## Summary Table

| Method | Requires SYS_FAILURE_EN? | Difficulty | Reliability |
|--------|-------------------------|------------|-------------|
| MAVSDK Python | ✅ YES | Medium | High* |
| PX4 Shell Command | ❌ NO | Low | Very High |
| ROS 2 Topic | ✅ YES | Medium | High |
| QGC Console | ✅ YES | Low | Medium |

*High reliability **only if** SYS_FAILURE_EN is properly enabled

## Quick Fix Right Now

The fastest way to test failsafes **immediately**:

```bash
# 1. Start your simulation
cd ~/sky_warrior_ws/src/skyw_simulation/new-method
./1_start_gazebo.sh
./2_spawn_px4_sitl.sh 1

# 2. In another terminal, use the PX4 command method
cd ~/sky_warrior_ws/src/failsafes/scripts
./test_gps_failsafe_px4cmd.sh

# 3. Follow the interactive prompts
```

This bypasses all the MAVSDK/parameter issues and works immediately!

## For Future Tests

To enable failure injection permanently:

```bash
# Add to your PX4 startup script
echo "param set SYS_FAILURE_EN 1" >> ~/PX4-Autopilot/build/px4_sitl_default/rootfs/0/etc/rc.txt

# OR: Create a custom params file
cat > ~/PX4-Autopilot/build/px4_sitl_default/rootfs/0/etc/params << EOF
SYS_FAILURE_EN 1
EOF
```

## References

- PX4 Source: `src/modules/mavlink/mavlink_receiver.cpp` (line with MAV_CMD_INJECT_FAILURE)
- PX4 Failure Module: `src/systemcmds/failure/failure.cpp`
- PX4 Docs: https://docs.px4.io/main/en/debug/failure_injection.html

## Still Having Issues?

If you still get TIMEOUT after enabling SYS_FAILURE_EN:

1. **Restart PX4 completely** (kill all px4 processes and restart)
2. **Check PX4 version:** Failure injection was added in v1.12+
3. **Use the PX4 shell method** as a reliable alternative
4. **Check MAVLink connection:** Ensure MAVSDK is connecting properly (you said it is)

The updated `test_failsafe_mavsdk.py` script now handles most of these issues automatically!
