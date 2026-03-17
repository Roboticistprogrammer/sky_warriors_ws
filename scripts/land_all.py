#!/usr/bin/env python3
import asyncio
from mavsdk import System

async def land_drone(sys_addr: str, drone_id: int, grpc_port: int):
    drone = System(port=grpc_port)
    await drone.connect(system_address=sys_addr)
    # Wait for connection
    async for state in drone.core.connection_state():
        if state.is_connected:
            break
    print(f"Drone {drone_id}: Landing...")
    try:
        await drone.action.land()
    except Exception as e:
        print(f"Drone {drone_id}: Land command failed: {e}")

async def main():
    drones = [
        ("udp://:14541", 1, 50060),
        ("udp://:14542", 2, 50061),
        ("udp://:14543", 3, 50062)
    ]
    await asyncio.gather(*(land_drone(addr, d_id, p) for addr, d_id, p in drones))

if __name__ == "__main__":
    asyncio.run(main())
