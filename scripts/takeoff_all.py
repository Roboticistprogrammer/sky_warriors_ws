#!/usr/bin/env python3
import asyncio
from mavsdk import System

async def takeoff_drone(sys_addr: str, drone_id: int, grpc_port: int, altitude: float = 10.0):
    drone = System(port=grpc_port)
    print(f"Drone {drone_id}: Connecting on {sys_addr} (GRPC port {grpc_port})...")
    await drone.connect(system_address=sys_addr)

    # Wait for connection
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone {drone_id}: Connected!")
            break

    # Wait for GPS lock
    print(f"Drone {drone_id}: Waiting for global position...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print(f"Drone {drone_id}: Global position estimate OK.")
            break

    # Arm
    print(f"Drone {drone_id}: Arming...")
    try:
        await drone.action.arm()
    except Exception as e:
        print(f"Drone {drone_id}: Failed to arm: {e}")
        return

    # Takeoff
    print(f"Drone {drone_id}: Taking off to {altitude}m...")
    try:
        await drone.action.set_takeoff_altitude(altitude)
        await drone.action.takeoff()
    except Exception as e:
        print(f"Drone {drone_id}: Failed to takeoff: {e}")

async def main():
    drones = [
        ("udp://:14541", 1, 50051),
        ("udp://:14542", 2, 50052),
        ("udp://:14543", 3, 50053)
    ]

    tasks = []
    for addr, drone_id, grpc_port in drones:
        tasks.append(takeoff_drone(addr, drone_id, grpc_port))

    await asyncio.gather(*tasks)
    print("\nTakeoff commands sent to all drones.")

if __name__ == "__main__":
    asyncio.run(main())
