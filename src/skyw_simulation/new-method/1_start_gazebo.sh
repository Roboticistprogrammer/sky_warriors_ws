#!/bin/bash
# Start Gazebo Harmonic with warehouse1 world
# Run this first before starting PX4 SITL instances

set -e

WORKSPACE_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo "=========================================="
echo "Starting Gazebo Harmonic - warehouse1"
echo "=========================================="
echo ""

# Source environment variables
source "${WORKSPACE_DIR}/gz_env.sh"

echo "Environment Variables:"
echo "  GZ_SIM_RESOURCE_PATH: $GZ_SIM_RESOURCE_PATH"
echo "  GZ_SIM_SYSTEM_PLUGIN_PATH: $GZ_SIM_SYSTEM_PLUGIN_PATH"
echo ""

# Start Gazebo with warehouse1 world
echo "Starting Gazebo..."
echo "World: warehouse1.sdf"
echo ""

gz sim "${WORKSPACE_DIR}/world/warehouse1.sdf"
