#!/bin/bash
# Alternative: Spawn PX4 SITL using make command (as described in the forum post)
# Run this AFTER Gazebo is already running (1_start_gazebo.sh)
#
# This uses: PX4_GZ_STANDALONE=1 PX4_GZ_WORLD=warehouse1 make px4_sitl gz_x500

set -e

VEHICLE_MODEL=${1:-x500}
INSTANCE=${2:-0}
WORKSPACE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PX4_DIR="${HOME}/PX4-Autopilot"

echo "=========================================="
echo "Spawning PX4 SITL via Make Command"
echo "=========================================="
echo "Vehicle Model: gz_${VEHICLE_MODEL}"
echo "Instance: $INSTANCE"
echo "World: warehouse1"
echo ""

# Source environment variables (CRITICAL for make command)
source "${WORKSPACE_DIR}/gz_env.sh"

# Check if Gazebo is running
if ! pgrep -f "gz sim" > /dev/null; then
    echo "ERROR: Gazebo is not running!"
    echo "Please run 1_start_gazebo.sh first in another terminal"
    exit 1
fi

echo "✓ Gazebo is running"
echo ""

echo "Environment Variables:"
echo "  PX4_GZ_STANDALONE: 1"
echo "  PX4_GZ_WORLD: warehouse1"
echo "  GZ_SIM_RESOURCE_PATH: $GZ_SIM_RESOURCE_PATH"
echo "  GZ_SIM_SYSTEM_PLUGIN_PATH: $GZ_SIM_SYSTEM_PLUGIN_PATH"
echo ""

cd "$PX4_DIR"

# Set position for instance
x_pos=$((INSTANCE * 4))
y_pos=0

echo "Spawning vehicle at position ($x_pos, $y_pos)..."
echo ""

# Run make command with proper environment
PX4_GZ_STANDALONE=1 \
PX4_GZ_WORLD=warehouse1 \
PX4_GZ_MODEL_POSE="$x_pos,$y_pos" \
make px4_sitl gz_${VEHICLE_MODEL}
