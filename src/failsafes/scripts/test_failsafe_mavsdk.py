#!/usr/bin/env python3
"""
Automated Failsafe Testing using MAVSDK
Requires: pip install mavsdk
"""

import asyncio
from mavsdk import System
from mavsdk.failure import FailureUnit, FailureType
from mavsdk.param import Param
import time


class FailsafeTester:
    def __init__(self, connection_url="udpin://0.0.0.0:14540"):
        self.drone = System()
        self.connection_url = connection_url
        
    async def connect(self):
        """Connect to the drone"""
        print(f"Connecting to drone at {self.connection_url}...")
        await self.drone.connect(system_address=self.connection_url)
        
        print("Waiting for drone to connect...")
        async for state in self.drone.core.connection_state():
            if state.is_connected:
                print("Drone connected!")
                break
                
    async def check_and_enable_failure_injection(self):
        """Check and enable SYS_FAILURE_EN parameter"""
        print("\nChecking SYS_FAILURE_EN parameter...")
        try:
            # Get current value
            result = await self.drone.param.get_param_int("SYS_FAILURE_EN")
            print(f"Current SYS_FAILURE_EN value: {result}")
            
            if result == 0:
                print("⚠️  SYS_FAILURE_EN is disabled. Enabling it...")
                await self.drone.param.set_param_int("SYS_FAILURE_EN", 1)
                print("✅ SYS_FAILURE_EN enabled!")
                
                # Verify
                result = await self.drone.param.get_param_int("SYS_FAILURE_EN")
                print(f"Verified SYS_FAILURE_EN value: {result}")
            else:
                print("✅ SYS_FAILURE_EN is already enabled!")
                
        except Exception as e:
            print(f"❌ Error checking/setting parameter: {e}")
            print("   You may need to set it manually in PX4 console:")
            print("   param set SYS_FAILURE_EN 1")
            print("   param save")
            raise
                
    async def wait_for_ready(self):
        """Wait for drone to be ready"""
        print("Waiting for drone to be ready...")
        async for health in self.drone.telemetry.health():
            if health.is_global_position_ok and health.is_home_position_ok:
                print("Drone is ready!")
                break
                
    async def arm_and_takeoff(self, altitude=10.0):
        """Arm drone and takeoff to specified altitude"""
        print("Arming...")
        await self.drone.action.arm()
        
        print(f"Taking off to {altitude}m...")
        await self.drone.action.set_takeoff_altitude(altitude)
        await self.drone.action.takeoff()
        
        # Wait for altitude
        await asyncio.sleep(10)
        print("Takeoff complete")
        
    async def inject_gps_failure(self):
        """Inject GPS failure"""
        print("\n" + "="*50)
        print("INJECTING GPS FAILURE")
        print("="*50)
        
        try:
            result = await asyncio.wait_for(
                self.drone.failure.inject(
                    FailureUnit.SENSOR_GPS,
                    FailureType.OFF,
                    0  # instance
                ),
                timeout=5.0  # 5 second timeout
            )
            print(f"✅ GPS failure injected! Result: {result}")
        except asyncio.TimeoutError:
            print("❌ TIMEOUT: PX4 did not respond to failure injection")
            print("\n🔍 TROUBLESHOOTING:")
            print("   1. Check if SYS_FAILURE_EN parameter is enabled:")
            print("      - In QGC: Parameters -> SYS_FAILURE_EN = 1")
            print("      - In PX4 console: param set SYS_FAILURE_EN 1; param save")
            print("\   2. Restart PX4 SITL after setting the parameter")
            print("   3. Check if you're using the correct PX4 version (v1.14+)")
            print("\n⚠️  CONTINUING WITH ALTERNATIVE METHOD...")
            raise
        except Exception as e:
            print(f"❌ Error injecting GPS failure: {e}")
            raise
        
    async def inject_battery_failure(self):
        """Inject battery failure"""
        print("\n" + "="*50)
        print("INJECTING BATTERY FAILURE")
        print("="*50)
        
        await self.drone.failure.inject(
            FailureUnit.SENSOR_BATTERY,
            FailureType.OFF,
            0
        )
        print("Battery failure injected!")
        
    async def inject_barometer_failure(self):
        """Inject barometer failure"""
        print("\n" + "="*50)
        print("INJECTING BAROMETER FAILURE")
        print("="*50)
        
        await self.drone.failure.inject(
            FailureUnit.SENSOR_BARO,
            FailureType.OFF,
            0
        )
        print("Barometer failure injected!")
        
    async def inject_magnetometer_failure(self):
        """Inject magnetometer failure"""
        print("\n" + "="*50)
        print("INJECTING MAGNETOMETER FAILURE")
        print("="*50)
        
        await self.drone.failure.inject(
            FailureUnit.SENSOR_MAG,
            FailureType.OFF,
            0
        )
        print("Magnetometer failure injected!")
        
    async def monitor_flight_mode(self, duration=30):
        """Monitor flight mode for specified duration"""
        print(f"\nMonitoring flight mode for {duration} seconds...")
        start_time = time.time()
        
        async for flight_mode in self.drone.telemetry.flight_mode():
            elapsed = time.time() - start_time
            print(f"[{elapsed:.1f}s] Flight Mode: {flight_mode}")
            
            if elapsed > duration:
                break
                
    async def monitor_position(self, duration=30):
        """Monitor position for specified duration"""
        print(f"\nMonitoring position for {duration} seconds...")
        start_time = time.time()
        
        async for position in self.drone.telemetry.position():
            elapsed = time.time() - start_time
            print(f"[{elapsed:.1f}s] Lat: {position.latitude_deg:.6f}, "
                  f"Lon: {position.longitude_deg:.6f}, "
                  f"Alt: {position.relative_altitude_m:.2f}m")
            
            if elapsed > duration:
                break
                
    async def test_gps_loss_failsafe(self):
        """Test GPS loss during flight"""
        print("\n" + "#"*60)
        print("# TEST: GPS LOSS FAILSAFE")
        print("#"*60)
        
        await self.connect()
        
        # CRITICAL: Check and enable failure injection parameter
        await self.check_and_enable_failure_injection()
        
        await self.wait_for_ready()
        await self.arm_and_takeoff(altitude=10.0)
        
        # Fly for a bit
        print("\nFlying normally for 10 seconds...")
        await asyncio.sleep(10)
        
        # Inject GPS failure
        try:
            await self.inject_gps_failure()
        except Exception:
            print("\n" + "!"*60)
            print("AUTOMATED FAILURE INJECTION FAILED!")
            print("Please use manual method:")
            print("!"*60)
            print("\n1. Open a new terminal")
            print("2. Connect to PX4:")
            print("   cd ~/PX4-Autopilot")
            print("   pxh> failure gps off")
            print("\n3. OR use QGC MAVLink console")
            print("\nWaiting 60 seconds for you to inject manually...")
            await asyncio.sleep(60)
        
        # Monitor response
        print("\nMonitoring failsafe response...")
        await self.monitor_flight_mode(duration=30)
        
        print("\nTest complete!")
        
    async def test_battery_failsafe(self):
        """Test battery failsafe"""
        print("\n" + "#"*60)
        print("# TEST: BATTERY FAILSAFE")
        print("#"*60)
        
        await self.connect()
        await self.wait_for_ready()
        await self.arm_and_takeoff(altitude=10.0)
        
        # Fly for a bit
        print("\nFlying normally for 10 seconds...")
        await asyncio.sleep(10)
        
        # Inject battery failure
        await self.inject_battery_failure()
        
        # Monitor response
        await self.monitor_flight_mode(duration=30)
        
        print("\nTest complete!")


async def main():
    """Main test runner"""
    tester = FailsafeTester("udpin://0.0.0.0:14540")
    
    print("""
    ╔════════════════════════════════════════════════════════╗
    ║        PX4 Failsafe Automated Testing Suite          ║
    ║              Gazebo Harmonic + PX4 1.17               ║
    ╚════════════════════════════════════════════════════════╝
    
    Available Tests:
    1. GPS Loss Failsafe
    2. Battery Failsafe
    3. Barometer Failsafe
    4. Magnetometer Failsafe
    
    Prerequisites:
    ✓ Gazebo Harmonic running with world loaded
    ✓ PX4 SITL instance running (listening on UDP port 14540)
    ✓ Drone spawned in simulation
    ✓ SYS_FAILURE_EN parameter set to 1 (will be checked automatically)
    
    CRITICAL FIX for TIMEOUT errors:
    =====================================
    If you get TIMEOUT errors, the issue is that SYS_FAILURE_EN
    parameter is not enabled in PX4. This script will try to enable
    it automatically, but if that fails, you need to:
    
    Option 1 - PX4 Console (Recommended):
    --------------------------------------
    1. While PX4 SITL is running, open another terminal
    2. Run: cd ~/PX4-Autopilot
    3. Connect: ./build/px4_sitl_default/bin/px4 shell
    4. Set parameter: param set SYS_FAILURE_EN 1
    5. Save: param save
    6. Restart this test
    
    Option 2 - QGroundControl:
    ---------------------------
    1. Open QGC -> Vehicle Setup -> Parameters
    2. Search for: SYS_FAILURE_EN
    3. Set value to: 1
    4. Restart PX4 SITL
    
    Option 3 - Edit params file:
    -----------------------------
    Edit: ~/PX4-Autopilot/build/px4_sitl_default/rootfs/0/etc/params
    Add: SYS_FAILURE_EN 1
    
    """)
    
    # Run GPS loss test
    try:
        await tester.test_gps_loss_failsafe()
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        print("\nSee troubleshooting steps above.")
        
    # Uncomment to run other tests:
    # await tester.test_battery_failsafe()


if __name__ == "__main__":
    print("Starting MAVSDK Failsafe Tests...")
    asyncio.run(main())
