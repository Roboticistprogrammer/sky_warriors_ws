#!/bin/bash

set -e

session="swarm"
WS_DIR="${HOME}/sky_warrior_ws"
ROS_SETUP="/opt/ros/humble/setup.bash"
WS_SETUP="${WS_DIR}/install/setup.bash"
DRONE_COUNT="${DRONE_COUNT:-3}"
SWARM_NAMESPACE="${SWARM_NAMESPACE:-}"
USE_FASTDDS_XML="${USE_FASTDDS_XML:-false}"
LAUNCH_FILE="${LAUNCH_FILE:-swarm_launch.py}"
START_CLIENT="${START_CLIENT:-true}"
START_CONTROLLER="${START_CONTROLLER:-true}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FASTDDS_XML="${SCRIPT_DIR}/config/fastdds.xml"

echo "Workspace directory: ${WS_DIR}"
echo "Session name: ${session}"
echo "Fast DDS profile: ${FASTDDS_XML}"

if [ ! -f "${ROS_SETUP}" ]; then
	echo "[ERROR] ROS setup file not found: ${ROS_SETUP}" >&2
	exit 1
fi

if [ ! -f "${FASTDDS_XML}" ]; then
	echo "[ERROR] Fast DDS profile not found: ${FASTDDS_XML}" >&2
	exit 1
fi

# If the session already exists, just attach to it
if tmux has-session -t "${session}" 2>/dev/null; then
	echo "tmux session '${session}' already exists. Attaching..."
	exec tmux attach -t "${session}"
fi

echo "Starting new tmux session '${session}'..."

tmux new-session -d -s "${session}" -n "Swarm" \
	"export RMW_IMPLEMENTATION=\"${RMW_IMPLEMENTATION:-rmw_fastrtps_cpp}\" && source \"${ROS_SETUP}\" && if [ -f \"${WS_SETUP}\" ]; then source \"${WS_SETUP}\"; fi && \
	ros2 launch skyw_swarm \"${LAUNCH_FILE}\" \
		drone_count:=${DRONE_COUNT} \
		start_client:=${START_CLIENT} \
		start_controller:=${START_CONTROLLER} \
		use_fastdds_xml:=${USE_FASTDDS_XML} \
		fastdds_xml:=\"${FASTDDS_XML}\" \
		namespace:=\"${SWARM_NAMESPACE}\"; \
	echo "[swarm.sh] Launch exited. Press Ctrl+D to close."; exec bash"

echo "tmux session '${session}' is ready."
exec tmux attach -t "${session}"

