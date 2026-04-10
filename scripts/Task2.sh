#!/bin/bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
ROS_SETUP="/opt/ros/humble/setup.bash"
WS_SETUP="${WS_DIR}/install/setup.bash"

if [ ! -f "${ROS_SETUP}" ]; then
	echo "[ERROR] ROS setup file not found: ${ROS_SETUP}" >&2
	exit 1
fi

if [ ! -f "${WS_SETUP}" ]; then
	echo "[ERROR] Workspace setup file not found: ${WS_SETUP}" >&2
	exit 1
fi

source "${ROS_SETUP}"
source "${WS_SETUP}"

# Formation controller is started by startup.sh as /swarm_controller.
# Note: PX4 uses NED coordinates (up is negative Z).

ros2 param set /swarm_controller formation_type arrow_head
ros2 param set /swarm_controller spacing 2.0
ros2 param set /swarm_controller rotation 90.0
ros2 param set /swarm_controller altitude -1.0

ros2 param set /swarm_controller leader_mode target
ros2 param set /swarm_controller leader_target_x 5.0
ros2 param set /swarm_controller leader_target_y 0.0
ros2 param set /swarm_controller leader_target_z -1.0
