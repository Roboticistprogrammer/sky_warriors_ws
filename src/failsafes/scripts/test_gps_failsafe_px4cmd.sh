#!/bin/bash
# GPS Failsafe Test using PX4's built-in failure command
# This bypasses MAVLink and directly uses PX4's internal command

echo "╔════════════════════════════════════════════════════════╗"
echo "║       GPS Failsafe Test (PX4 Command Method)          ║"
echo "║              Gazebo Harmonic + PX4 1.17                ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "This method uses PX4's built-in 'failure' command which is"
echo "more reliable than MAVLink-based injection."
echo ""

# Check if PX4 instance is running
if ! pgrep -f "px4.*-i 0" > /dev/null; then
    echo "❌ Error: No PX4 instance found running with -i 0"
    echo "Please start PX4 SITL first:"
    echo "  cd ~/sky_warrior_ws/src/skyw_simulation/new-method"
    echo "  ./2_spawn_px4_sitl.sh 1"
    exit 1
fi

echo "✅ PX4 instance detected"
echo ""

# Function to send PX4 command
send_px4_command() {
    local instance=$1
    local command=$2
    echo "Sending command to PX4 instance $instance: $command"
    
    # Method 1: Use pxh (PX4 shell)
    # This sends commands to the running PX4 instance
    cd ~/PX4-Autopilot
    echo "$command" | ./build/px4_sitl_default/bin/px4 shell -i $instance
}

echo "=========================================="
echo "Test Procedure:"
echo "=========================================="
echo ""
echo "Step 1: Arm and takeoff your drone using QGC or MAVSDK"
echo "        Manually arm and takeoff to ~10m altitude"
echo ""
echo "Press ENTER when drone is in the air and ready..."
read

echo ""
echo "Step 2: Injecting GPS failure in 3 seconds..."
sleep 1
echo "        2..."
sleep 1
echo "        1..."
sleep 1
echo ""
echo "==================================================
"
echo "INJECTING GPS FAILURE"
echo "==================================================
"

# Inject GPS failure
send_px4_command 0 "failure gps off"

if [ $? -eq 0 ]; then
    echo "✅ GPS failure command sent successfully!"
else
    echo "⚠️  Command may have failed. Check PX4 console output."
fi

echo ""
echo "Expected Behavior:"
echo "  - GPS status should change to: NOT FOUND or LOST"
echo "  - Flight mode should change to: RTL"
echo "  - Drone should return to launch position"
echo "  - Drone should land automatically"
echo ""
echo "=========================================="
echo "Monitoring (check QGroundControl):"
echo "=========================================="
echo "  - Flight Mode: Should switch to RTL"
echo "  - GPS Status: Should show error"
echo "  - Position estimate: May degrade"
echo ""
echo "To restore GPS (if needed):"
echo "  failure gps ok"
echo ""
echo "Waiting 60 seconds for observation..."
echo "(Press Ctrl+C to exit early)"

for i in {60..1}; do
    echo -ne "\rTime remaining: ${i}s  "
    sleep 1
done

echo ""
echo ""
echo "=========================================="
echo "Test Complete!"
echo "=========================================="
echo ""
echo "Did the drone execute RTL and land? (y/n)"
read response

if [ "$response" = "y" ] || [ "$response" = "Y" ]; then
    echo "✅ GPS FAILSAFE TEST: PASSED"
else
    echo "❌ GPS FAILSAFE TEST: FAILED or INCONCLUSIVE"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check PX4 logs: ~/PX4-Autopilot/build/px4_sitl_default/rootfs/0/log/*.ulg"
    echo "2. Verify failsafe parameters:"
    echo "   - COM_POS_FS_DELAY (position failsafe delay)"
    echo "   - NAV_RCL_ACT (RC loss action, affects GPS loss too)"
    echo "3. Check if drone had valid GPS lock before failure"
fi

echo ""
echo "To restore GPS for next test:"
send_px4_command 0 "failure gps ok"
echo ""
