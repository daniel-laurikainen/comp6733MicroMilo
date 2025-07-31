#!/usr/bin/env python3
import asyncio
import yaml
from pywizlight import wizlight, PilotBuilder

CONFIG_PATH = "config/bulbs.yaml"
RED_RGB = (255, 0, 0)

async def check_bulbs():
    # Load bulbs config
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    bulbs = config.get("bulbs", [])
    if not bulbs:
        print("[ERROR] No bulbs found in config.")
        return

    for bulb_info in bulbs:
        name = bulb_info.get("name")
        ip = bulb_info.get("ip")

        if not ip or not name:
            print(f"[WARNING] Skipping bulb with incomplete info: {bulb_info}")
            continue

        print(f"\n[INFO] Connecting to {name} at {ip} ...")
        bulb = wizlight(ip)

        try:
            # Turn bulb red
            await bulb.turn_on(PilotBuilder(rgb=RED_RGB, brightness=255))
            print(f"[SUCCESS] {name} turned RED. Press ENTER when ready to turn off and continue.")
            input()
            await bulb.turn_off()
            print(f"[INFO] {name} turned OFF.")
        except Exception as e:
            print(f"[ERROR] Failed to connect/control {name} at {ip}: {e}")

if __name__ == "__main__":
    asyncio.run(check_bulbs())
