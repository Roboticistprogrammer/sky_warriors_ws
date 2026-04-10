How to Structure a Polished, Systematic 10-Minute Video (Strict Single-Take Rules)
You must follow the guideline you shared exactly (no cuts, no editing, timer always visible, single real-time take).

Pre-Video Testing Plan (Do This First)
Test everything modularly so the video flows smoothly:

Package / Feature,Test Method (before recording),What to Show in Video:

Directory & code structure,Manually walk through every folder,Full explorer demo
Simulation environment launch,Write one-click launch script(s),Step-by-step launch
Camera feed + color detection,Run node → publish image topic,Live camera window
QR detection & decoding,Place test QR → decode & print command,Live detection
Formation control + rotation,3+ UAVs → switch line/arrowhead + rotate to target,Formation change + rotation
Pitch/Roll/Yaw maneuvers,Fixed-center tilt commands,All 3 maneuvers
Add/Remove agent (Task Allocation),QR command → specific UAV lands in colored zone,Key task allocation demo
Semi-autonomous single command,Joystick/keyboard → whole swarm moves together,Single input control
Full mission flow,Home → QR1 → QR2 … → return & land,End-to-end (or key parts)


1- Exact Video Recording Sequence (≈9–10 min total)
Launch Environment (startup.sh is launching 3 uav wolrd with XRCE terminal) + camera node + qr node + offboard node


2- Takeoff & do Formation flight in Line then move toward next point
(skyw_swarm is for formarion but has complicxated structure i need correct nodes and services to lanch then use skyw_control for offboard mode to go to wall1)


3- QR detection + decoding (show command being executed)
(skyw_detection package should be used)

4- Task allocation demo: Execute “remove UAV 2 → land in red zone”
Add agent back (if implemented)
Return to home + safe landing + disarm


TODO:

Pitch / Roll / Yaw maneuvers in formation (keep swarm center fixed)
Formation change (line → arrowhead → etc.)




