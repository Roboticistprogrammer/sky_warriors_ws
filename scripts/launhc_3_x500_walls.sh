#!/bin/bash
# File: launch_3_x500_walls.sh

cd ~/sky_warrior_ws

# Start first instance (starts Gazebo server)
PX4_GZ_WORLD=walls PX4_SYS_AUTOSTART=4001 PX4_SIM_MODEL=gz_x500 \
    ./build/px4_sitl_default/bin/px4 -i 1 &
sleep 3

# Start second instance
PX4_GZ_STANDALONE=1 PX4_GZ_WORLD=walls PX4_SYS_AUTOSTART=4001 \
    PX4_GZ_MODEL_POSE="3,0" PX4_SIM_MODEL=gz_x500 \
    ./build/px4_sitl_default/bin/px4 -i 2 &
sleep 2

# Start third instance
PX4_GZ_STANDALONE=1 PX4_GZ_WORLD=walls PX4_SYS_AUTOSTART=4001 \
    PX4_GZ_MODEL_POSE="6,0" PX4_SIM_MODEL=gz_x500 \
    ./build/px4_sitl_default/bin/px4 -i 3 &
sleep 2

# Start Micro-XRCE-DDS Agent
MicroXRCEAgent udp4 -p 8888
