#!/bin/bash
# Proper Multi-vehicle spawn for Gazebo Harmonic + PX4
# Sets up multiple drones in warehouse1 world

set -e

NUM_VEHICLES=${1:-3}
VEHICLE_MODEL=${2:-x500}
WORKSPACE_DIR="$(cd "$(dirname "$0")" && pwd)"
PX4_DIR="${HOME}/PX4-Autopilot"

echo "=========================================="
echo "Multi-Vehicle Setup for Gazebo Harmonic"
echo "=========================================="
echo "Vehicles: $NUM_VEHICLES | Model: $VEHICLE_MODEL"
echo ""

# Source environment
source "${WORKSPACE_DIR}/gz_env.sh"

# Cleanup function
cleanup() {
    echo ""
    echo "Cleaning up..."
    pkill -9 -f "px4.*-i" || true
    pkill -9 -f "gz sim" || true
    pkill -9 ruby || true
    sleep 1
}

trap cleanup EXIT SIGINT SIGTERM

# Clean any existing instances
cleanup

cd "$PX4_DIR"

echo "Starting vehicles..."
echo ""

# Important: For first instance, DO NOT use standalone mode
# This allows subsequent instances to connect to the same gz server

for i in $(seq 0 $((NUM_VEHICLES - 1))); do
    x_pos=$((i * 4))
    y_pos=0
    
    echo "[$i] Spawning at ($x_pos, $y_pos)..."
    
    if [ $i -eq 0 ]; then
        # First vehicle: Starts gz server with world file
        echo "  Starting gz server with warehouse1 world..."
        
        PX4_SYS_AUTOSTART=4001 \
        PX4_GZ_MODEL_POSE="$x_pos,$y_pos" \
        PX4_GZ_MODEL="${VEHICLE_MODEL}" \
        PX4_GZ_WORLD="warehouse1" \
        ./build/px4_sitl_default/bin/px4 -i $i &
        
        echo "  Waiting 15s for gz server and first model..."
        sleep 15
        
        # Verify gz is running
        if ! pgrep -f "gz sim" > /dev/null; then
            echo "ERROR: gz sim not running!"
            exit 1
        fi
        echo "  ✓ gz server running"
        
    else
        # Subsequent vehicles: Connect to existing gz server
        echo "  Connecting to existing gz server..."
        
        PX4_SYS_AUTOSTART=4001 \
        PX4_SIM_SPEED_FACTOR=0.1\
        PX4_GZ_MODEL_POSE="$x_pos,$y_pos" \
        PX4_GZ_MODEL="${VEHICLE_MODEL}" \
        ./build/px4_sitl_default/bin/px4 -i $i &
        
        echo "  Waiting 5s..."
        sleep 5
    fi
done

echo ""
echo "=========================================="
echo "All vehicles launched!"
echo "=========================================="
echo ""

# Give sensors time to initialize
echo "Waiting 10s for sensors to initialize..."
sleep 10

# Status check
echo ""
echo "Status Check:"
echo "-------------"
echo ""

echo "PX4 Instances:"
pgrep -a -f "px4.*-i" | nl

echo ""
echo "Gazebo Models:"
timeout 5 gz model --list 2>&1 | grep "x500" || echo "  Could not list models (might still be loading)"

echo ""
echo "MAVLink Ports:"
for i in $(seq 0 $((NUM_VEHICLES - 1))); do
    port=$((14540 + i))
    if netstat -tuln 2>/dev/null | grep -q ":$port "; then
        echo "  ✓ Vehicle $i: UDP $port"
    else
        echo "  ✗ Vehicle $i: UDP $port not active"
    fi
done

echo ""
echo "=========================================="
echo "Connect QGC to ports: 14540-$((14540+NUM_VEHICLES-1))"
echo "Logs: $PX4_DIR/build/px4_sitl_default/rootfs/*/out.log"
echo "Press Ctrl+C to stop"
echo "=========================================="

# Keep running
wait
