#!/bin/bash

set -e

session="px4-sitl"
PX4_DIR="${HOME}/PX4-Autopilot"
PX4_BIN="${PX4_DIR}/build/px4_sitl_default/bin/px4"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/gz_env.sh"
SKYW_WORLD_NAME="skyw_hexagon"
SKYW_WORLD_FILE="${PX4_DIR}/Tools/simulation/gz/worlds/${SKYW_WORLD_NAME}.sdf"

echo "PX4 directory: ${PX4_DIR}"
echo "Session name: ${session}"
echo "Gazebo world: ${SKYW_WORLD_FILE}"

if [ ! -x "${PX4_BIN}" ]; then
	echo "[ERROR] PX4 binary not found or not executable: ${PX4_BIN}" >&2
	exit 1
fi

if [ ! -f "${SKYW_WORLD_FILE}" ]; then
	echo "[ERROR] World file not found: ${SKYW_WORLD_FILE}" >&2
	exit 1
fi


if tmux has-session -t "${session}" 2>/dev/null; then
	echo "tmux session '${session}' already exists. Attaching..."
	exec tmux attach -t "${session}"
fi

echo "Starting new tmux session '${session}'..."

tmux new-session -d -s "${session}" -n "PX4-1" \
	"cd \"${PX4_DIR}\" && unset PX4_GZ_STANDALONE; PX4_SYS_AUTOSTART=4010 PX4_GZ_WORLD=${SKYW_WORLD_NAME} PX4_GZ_MODEL_POSE=\"-7,5\" PX4_SIM_MODEL=gz_x500_mono_cam_down \"${PX4_BIN}\" -i 1"

sleep 12

tmux new-window -t "${session}:" -n "PX4-2" \
	"cd \"${PX4_DIR}\" && PX4_GZ_STANDALONE=1 PX4_SYS_AUTOSTART=4001 PX4_GZ_MODEL_POSE=\"-7,4\" PX4_SIM_MODEL=gz_x500 \"${PX4_BIN}\" -i 2"

tmux new-window -t "${session}:" -n "PX4-3" \
	"cd \"${PX4_DIR}\" && PX4_GZ_STANDALONE=1 PX4_SYS_AUTOSTART=4001 PX4_GZ_MODEL_POSE=\"-7,6\" PX4_SIM_MODEL=gz_x500 \"${PX4_BIN}\" -i 3"

tmux new-window -t "${session}:" -n "MicroXRCE" \
	"MicroXRCEAgent udp4 -p 8888"

echo "tmux session '${session}' is ready."
exec tmux attach -t "${session}"
