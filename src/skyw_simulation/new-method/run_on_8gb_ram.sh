#!/bin/bash
# Quick launcher for 8GB RAM systems
# This uses optimal settings to prevent sensor errors

NUM_VEHICLES=${1:-1}
VEHICLE_MODEL=${2:-x500}

echo "=========================================="
echo "8GB RAM Optimized Launch"
echo "=========================================="
echo "Vehicles: $NUM_VEHICLES"
echo "Model: $VEHICLE_MODEL"
echo "Speed Factor: 0.5 (optimized for low RAM)"
echo ""
echo "---"
echo "This script calls 2_spawn_px4_sitl.sh with"
echo "speed factor 0.5 and extended wait times."
echo "=========================================="
echo ""

# Call the main script with speed factor 0.5
./2_spawn_px4_sitl.sh "$NUM_VEHICLES" "$VEHICLE_MODEL" 0.5
