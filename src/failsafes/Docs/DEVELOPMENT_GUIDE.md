# Failsafe Testing: Development Path Analysis


## Notes:
Failure injection is disabled by default, and can be enabled using the SYS_FAILURE_EN parameter.

check mavsdk failure API[https://mavsdk.mavlink.io/main/en/cpp/api_reference/classmavsdk_1_1_failure.html]


## Question: Can I copy PX4 MAVSDK tests and will they work?

**Short Answer**: No, copying directly won't work without significant modification.

**Why Not?**
1. **Gazebo Version Mismatch**: PX4 MAVSDK tests are hard-coded for `gazebo-classic`, not `gz` (Harmonic)
2. **Build System**: Requires C++ compilation with MAVSDK library and Catch2 framework
3. **Infrastructure Dependencies**: Expects specific PX4 build artifacts and test runner framework

## Development Effort Comparison

### Option 1: Port MAVSDK Tests to Gz Harmonic ⚠️ HIGH EFFORT
**Estimated Time**: 2-4 weeks of development
**Complexity**: High

**What's Required:**
```
1. Modify test infrastructure (~/PX4-Autopilot/test/mavsdk_tests/integration_test_runner/)
   - Update process_helper.py to use 'gz' instead of 'gazebo-classic'
   - Update environment variables for Gazebo Harmonic
   - Modify model spawning logic

2. Build MAVSDK tests in PX4:
   cd ~/PX4-Autopilot
   DONT_RUN=1 make px4_sitl gz_x500 mavsdk_tests
   
3. Update test configurations (configs/sitl.json)
   - Change "simulator": "gazebo" to "simulator": "gz"
   - Update model names (iris -> x500, etc.)
   - Adjust world paths

4. Test and debug each test case
   - GPS loss tests
   - Battery failsafe tests
   - Sensor failure tests
```

**Pros:**
- Comprehensive automated testing
- Established test framework
- CI/CD integration possible

**Cons:**
- Requires deep knowledge of PX4 build system
- Time-consuming setup
- Maintenance burden when PX4 updates

---

### Option 2: Manual Testing with Scripts ✅ LOW EFFORT (IMPLEMENTED)
**Estimated Time**: Already done! (see failsafes/scripts/)
**Complexity**: Low

**What's Provided:**
```
failsafes/
├── README.md                              # Overview and references
├── parameters/
│   └── failsafe_params.yaml              # All relevant parameters
└── scripts/
    ├── test_gps_loss.sh                  # GPS failure test guide
    ├── test_battery_failsafe.sh          # Battery test guide
    ├── test_rc_loss.sh                   # RC loss test guide
    ├── test_datalink_loss.sh             # Telemetry loss test
    ├── test_failsafe_mavsdk.py           # Automated Python/MAVSDK tests
    └── failsafe_monitor_ros2.py          # ROS 2 monitoring node
```

**How to Use:**
```bash
# 1. Start your simulation
cd ~/sky_warrior_ws/src/skyw_simulation/new-method
./1_start_gazebo.sh
./2_spawn_px4_sitl.sh 1

# 2. Monitor failsafes (Terminal 1)
cd ~/sky_warrior_ws/src/failsafes/scripts
python3 failsafe_monitor_ros2.py

# 3. Run test (Terminal 2)
./test_gps_loss.sh                        # Follow manual steps
# OR
python3 test_failsafe_mavsdk.py           # Automated (requires: pip install mavsdk)
```

**Pros:**
- Immediate use - ready now
- Easy to understand and modify
- Works with your existing Gz Harmonic setup
- No complex build requirements

**Cons:**
- Manual verification needed (unless using MAVSDK python script)
- Less formal than unit tests
- Requires QGroundControl or MAVSDK for monitoring

---

### Option 3: Hybrid Approach 🔧 MEDIUM EFFORT
**Estimated Time**: 1-2 days
**Complexity**: Medium

**Approach:**
1. Use provided manual scripts for initial testing
2. Develop Python automation using MAVSDK (test_failsafe_mavsdk.py as template)
3. Add ROS 2 integration for CI/CD if needed

**Benefits:**
- Best of both worlds
- Automated without heavy PX4 build system
- ROS 2 native integration

---

## Recommended Path for Sky Warrior Project

### Phase 1: Immediate Testing (NOW) ✅
```bash
# Use the provided scripts in failsafes/scripts/
# Enable failure injection in PX4:
param set SYS_FAILURE_EN 1
param save

# Run tests following the script guides
```

### Phase 2: Automation (1-2 weeks)
```bash
# Install MAVSDK Python
pip install mavsdk

# Enhance test_failsafe_mavsdk.py for your specific scenarios
# Add swarm-specific failsafe tests
```

### Phase 3: Integration (optional)
```bash
# If you need CI/CD with automated testing:
# - Create ROS 2 launch files for automated test execution
# - Log results to files for analysis
# - Consider lightweight pytest framework instead of full MAVSDK C++
```

---

## Key Failsafe Parameters to Test

For each drone in your swarm, verify these failsafes:

1. **GPS Loss** → RTL and land
2. **Battery Low** → RTL when < 15%, land when < 7%
3. **Datalink Loss** → Continue mission or RTL (configurable)
4. **Geofence Breach** → RTL or Hold
5. **Swarm-Specific**: Leader loss → follower behavior

See `parameters/failsafe_params.yaml` for complete parameter list.

---

## Answer to Your Original Question

> "If I copy and paste some of these scripts to my failsafe folder would it work or does it have a long development process?"

**Answer**: 
- ❌ Copying PX4's C++ MAVSDK tests = Won't work directly, requires 2-4 weeks of porting effort
- ✅ Using the scripts I've created for you = Works NOW with your Gz Harmonic setup
- ✅ Python MAVSDK automation = Works with minimal setup (pip install mavsdk)

**Recommendation**: Start with the provided manual test scripts and Python MAVSDK script. They're designed specifically for Gazebo Harmonic + PX4 1.17 and your workspace structure. You can have comprehensive failsafe testing running today, not weeks from now.

---

## Quick Start

```bash
# 1. Review the main README
cat ~/sky_warrior_ws/src/failsafes/README.md

# 2. Check parameters
cat ~/sky_warrior_ws/src/failsafes/parameters/failsafe_params.yaml

# 3. Run a test
cd ~/sky_warrior_ws/src/failsafes/scripts
./test_gps_loss.sh

# 4. For automated testing (install mavsdk first)
pip install mavsdk
python3 test_failsafe_mavsdk.py
```

Good luck with your failsafe testing! 🚁
