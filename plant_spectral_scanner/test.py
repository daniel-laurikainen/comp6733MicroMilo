import asyncio
from pywizlight import wizlight, PilotBuilder
import time

async def toggle_bulb():
    bulb = wizlight("192.168.117.19")  # Replace with your bulb's IP

    colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255)
    }

    for color_name, rgb in colors.items():
        print(f"\n[INFO] Preparing to turn bulb ON with {color_name}...")

        start_time = time.time()
        await bulb.turn_on(PilotBuilder(rgb=rgb, brightness=255))
        print(f"[COMMAND SENT] Bulb set to {color_name}.")
        
        input("Press ENTER when you see the light turn ON...")  # Wait for user

        reaction_time = time.time() - start_time
        print(f"[RESULT] Time from command to visual ON: {reaction_time:.3f} seconds")

        await asyncio.sleep(1)
        print("[INFO] Turning bulb OFF...")
        await bulb.turn_off()
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(toggle_bulb())
