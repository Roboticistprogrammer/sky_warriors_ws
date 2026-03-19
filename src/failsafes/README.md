# Failsafe Testing for Sky Warrior

This folder now uses a simple setup with only two scripts:

- `scripts/failsafe_manager.py` (core MAVSDK helper class)
- `scripts/mavsdkrunner.py` (interactive test runner)

## What each script does

### `failsafe_manager.py`
Handles all low-level MAVSDK actions:
- connect to PX4
- enable `SYS_FAILURE_EN`
- arm and take off
- inject and restore failures
- wait for flight mode changes like `RETURN_TO_LAUNCH` and `LAND`

### `mavsdkrunner.py`
Shows a menu of failure scenarios and runs them step-by-step.

## Quick start

1. Start your Gazebo/PX4 simulation.
2. Go to:

```bash
cd ~/sky_warriors_ws/src/failsafes/scripts
```

3. Run:

```bash
python3 mavsdkrunner.py
```

4. Pick a test from the menu.

## Important notes

- Default connection in runner is `udpin://0.0.0.0:14541`.
- `SYS_FAILURE_EN` must be `1` (the manager tries to enable it).
- Some failures are not supported by all PX4 builds. If unsupported, the run is skipped safely.

## Multi-drone RTL landing zones (skyw_multi_lz_world)

For Gazebo Harmonic `skyw_multi_lz_world`, these LZ coordinates are used:

- Drone `0` -> `(0, 0)`
- Drone `1` -> `(4, 3)`
- Drone `2` -> `(8, 0)`

So when RTL is triggered, each drone returns to its own landing zone.
