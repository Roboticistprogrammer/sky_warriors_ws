#!/usr/bin/env python3
import asyncio
from mavsdk import System

async def check_drone_status(sys_addr: str, drone_id: int, grpc_port: int):
    drone = System(port=grpc_port)
    try:
        await asyncio.wait_for(drone.connect(system_address=sys_addr), timeout=5.0)
        
        # Wait for connection
        async for state in drone.core.connection_state():
            if state.is_connected:
                break
        
        # Get various states
        is_armed = False
        async for armed in drone.telemetry.armed():
            is_armed = armed
            break
            
        flight_mode = "Unknown"
        async for mode in drone.telemetry.flight_mode():
            flight_mode = mode.name
            break
            
        landed_state = "Unknown"
        async for state in drone.telemetry.landed_state():
            landed_state = state.name
            break

        print(f"Drone {drone_id}: Armed={is_armed}, Mode={flight_mode}, Landed={landed_state}")
        
    except Exception as e:
        print(f"Drone {drone_id}: Failed to check status: {e}")

async def main():
    drones = [
        ("udp://:14541", 1, 50054),
        ("udp://:14542", 2, 50055),
        ("udp://:14543", 3, 50056)
    ]

    tasks = []
    for addr, drone_id, grpc_port in drones:
        tasks.append(check_drone_status(addr, drone_id, grpc_port))

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
