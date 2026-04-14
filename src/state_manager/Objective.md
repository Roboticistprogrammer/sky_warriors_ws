2. Implementation Steps
Launch Multiple Drones: Create a launch file that spawns several instances of your drone model. Use the <group ns="uav_name"> tag to wrap each spawn script so that topics like /cmd_vel are prefixed (e.g., /uav1/cmd_vel).
Coordination Script: Develop a central "Swarm Manager" node or run local "Coordination Scripts" on each drone. These scripts should exchange position data via MAVLink or ROS topics to maintain formation.
Dispatch Logic: Implement a "state switch" in your control node. When a dispatch condition is met (e.g., a specific task assigned to UAV3), the node should:
Stop following the swarm's collective setpoint.
Command a new independent waypoint.
Notify the swarm manager to re-calculate formation for the remaining 
 drones.
 
 
 IDEA:
 state_manager (keep & upgrade to state-machine)
Node: drone_state_manager (run once per drone under its namespace /uavX/)
States (use enum or SMACH / simple rclpy state machine):

IN_SWARM
DETACHING → heading to colored zone
LANDING
WAITING (disarmed on ground)
REJOINING → takeoff + return to formation

Key functions / ROS interfaces:

Service server (the one you asked for):Pythonself.dispatch_srv = self.create_service(
    swarm_msgs.srv.DispatchDrone,
    'dispatch', self.handle_dispatch)Inside handle_dispatch(request):
Check if request.drone_id == self.my_id
If yes → change state to DETACHING
Use your existing detach logic + PX4 commands
Return success

Subscriptions:
/<drone>/qr_decoded (or a swarm-wide topic if you broadcast)
/<drone>/detected_landing_zone

Publishers (to PX4 via px4_msgs):
/fmu/in/vehicle_command
/fmu/in/offboard_mode
/fmu/in/trajectory_setpoint (or position setpoint)

Timer (10 Hz) → state_machine_loop() that executes the current state (send setpoints, arm/disarm, etc.).
