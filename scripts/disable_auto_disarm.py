#!/usr/bin/env python3
import asyncio
from mavsdk import System

async def disable_auto_disarm_for_drone(sys_addr: str, drone_id: int, grpc_port: int):
    drone = System(port=grpc_port)
    print(f"Drone {drone_id}: Connecting on {sys_addr} (GRPC port {grpc_port})...")
    await drone.connect(system_address=sys_addr)

    # Wait for connection
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"Drone {drone_id}: Connected!")
            break

    # Disable auto-disarm by setting COM_DISARM_PRFLT to -1 and COM_DISARM_LAND to -1
    print(f"Drone {drone_id}: Setting parameters to -1...")
    try:
        await drone.param.set_param_float("COM_DISARM_PRFLT", -1.0)
        await drone.param.set_param_float("COM_DISARM_LAND", -1.0)
        print(f"Drone {drone_id}: Successfully disabled preflight and landing auto-disarm.")
        
        # Verify
        val1 = await drone.param.get_param_float("COM_DISARM_PRFLT")
        val2 = await drone.param.get_param_float("COM_DISARM_LAND")
        print(f"Drone {drone_id}: Verified COM_DISARM_PRFLT = {val1}, COM_DISARM_LAND = {val2}")
    except Exception as e:
        print(f"Drone {drone_id}: Failed to set parameter: {e}")

async def main():
    # Ports for the 3 drones started by sitl_multiple_run.sh
    drones = [
        ("udp://:14541", 1, 50051),
        ("udp://:14542", 2, 50052),
        ("udp://:14543", 3, 50053)
    ]

    tasks = []
    for addr, drone_id, grpc_port in drones:
        tasks.append(disable_auto_disarm_for_drone(addr, drone_id, grpc_port))

    await asyncio.gather(*tasks)
    print("\nAll drones configured. They will no longer disarm automatically after being armed.")

if __name__ == "__main__":
    asyncio.run(main())
