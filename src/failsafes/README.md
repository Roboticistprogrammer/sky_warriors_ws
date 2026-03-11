# Failsafe Testing for Sky Warrior

This folder contains failsafe testing scripts and documentation for the Sky Warrior drone swarm.

## Overview

Testing failsafe behaviors using Gazebo Harmonic + PX4 1.17 with manual injection and ROS 2 integration.

## Testing Methods

### Method 1: MAVLink Commander (Simplest)
Use QGroundControl or MAVSDK to:
1. Arm and takeoff
2. Start mission/offboard mode
3. Inject failures via MAVLink commands
4. Observe failsafe response

### Method 2: ROS 2 Service Calls
Use PX4 ROS 2 topics to inject sensor failures programmatically.

### Method 3: Gazebo Plugin Manipulation
Directly manipulate sensor plugins in Gazebo Harmonic.

## Failsafe Types to Test

### 1. GPS Failure
- **Expected Behavior**: RTL -> Land if GPS lost during mission
- **Test Command**: See `scripts/test_gps_loss.sh`

### 2. Battery Low
- **Expected Behavior**: RTL when battery < threshold
- **Test Command**: Modify battery parameters

### 3. RC Loss
- **Expected Behavior**: Continue mission or RTL based on params
- **Parameters**: 
  - `COM_RCL_EXCEPT` - RC loss exceptions
  - `NAV_RCL_ACT` - RC loss action

### 4. Datalink Loss
- **Expected Behavior**: Continue for timeout, then RTL
- **Parameters**:
  - `COM_DL_LOSS_T` - Datalink loss time
  - `NAV_DLL_ACT` - Datalink loss action

### 5. Geofence Breach
- **Expected Behavior**: RTL or Land
- **Parameters**: `GF_ACTION`

## Quick Start

See individual test scripts in `scripts/` folder.

## References
- [PX4 Failsafe Documentation](https://docs.px4.io/main/en/config/safety.html)
- [PX4 Parameters Reference](https://docs.px4.io/main/en/advanced_config/parameter_reference.html)
