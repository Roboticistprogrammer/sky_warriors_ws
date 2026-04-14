How to Structure a Polished, Systematic 10-Minute Video (Strict Single-Take Rules)
You must follow the guideline you shared exactly (no cuts, no editing, timer always visible, single real-time take).
1. Pre-Video Testing Plan (Do This First)
Test everything modularly so the video flows smoothly:

Package / Feature,Test Method (before recording),What to Show in Video
Directory & code structure,Manually walk through every folder,Full explorer demo
Simulation environment launch,Write one-click launch script(s),Step-by-step launch
Camera feed + color detection,Run node → publish image topic,Live camera window
QR detection & decoding,Place test QR → decode & print command,Live detection
Formation control + rotation,3+ UAVs → switch line/arrowhead + rotate to target,Formation change + rotation
Pitch/Roll/Yaw maneuvers,Fixed-center tilt commands,All 3 maneuvers
Add/Remove agent (Task Allocation),QR command → specific UAV lands in colored zone,Key task allocation demo
Semi-autonomous single command,Joystick/keyboard → whole swarm moves together,Single input control
Full mission flow,Home → QR1 → QR2 … → return & land,End-to-end (or key parts)

2. Exact Video Recording Sequence (≈9–10 min total)

0:00 – Start recording (screen recorder only)
0:05 – Start timer (visible in corner for whole video)
0:10 – 2:30 Directory & Files (very important!)
Open file explorer
Slowly show every folder and file one by one (narrate: “This is the QR decoder package… this is the formation controller…”)
Zoom in on important files if needed

2:30 – 3:30 Launch Environment
Close explorer
Launch Gazebo/ROS2 step-by-step (show terminals)
Introduce custom vehicle models if you have any

3:30 – 9:00 Core Demonstrations (main part)
Takeoff with single command
Formation flight + formation rotation toward next point
QR detection + decoding (show command being executed)
Task allocation demo: Execute “remove UAV X → land in red zone”
Pitch / Roll / Yaw maneuvers in formation (keep swarm center fixed)
Formation change (line → arrowhead → etc.)
Semi-autonomous mode: switch to single joystick/keyboard control and fly the whole swarm
Add agent back (if implemented)
Return to home + safe landing + disarm

If anything is incomplete (last 30–60 s)
Stop simulation
Show on-screen text + explain:
“Current progress: … / Approach taken: … / Planned next steps: …”


Narration rules:

Use your own voice (clear, calm, slow).
Or add clean on-screen text descriptions.
Never use AI-generated voice.

3. Technical Tips for a Professional Look

Timer: Use a big, simple stopwatch (e.g. timer.google.com or Windows Clock app) placed in the top-right corner.
Recorder: OBS Studio (free) → set to 1080p or 1440p, 30–60 fps.
Clean desktop: Close everything except recorder + timer before starting.
Rehearse: Record 5–6 practice takes. The final one must be perfect (no mistakes, no “uhh”, within 10 min).
File size: Keep under ~2 GB (YouTube/Google Drive link is fine).

4. Quick Checklist Before Uploading

Timer visible entire video ✓
No cuts/edits/speed changes ✓
All folders/files shown one-by-one ✓
All required demos present (QR, maneuvers, rotation, add/remove, semi-autonomous) ✓
Task allocation shown via QR remove command ✓
