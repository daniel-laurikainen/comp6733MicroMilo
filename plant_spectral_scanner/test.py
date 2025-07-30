import asyncio
from pywizlight import wizlight, PilotBuilder

async def toggle_bulb():
    bulb = wizlight("192.168.119.60")  # Replace with actual IP
    print("Turning bulb ON...")
    await bulb.turn_on(PilotBuilder(brightness=255))
    print("Bulb should be ON.")

if __name__ == "__main__":
    asyncio.run(toggle_bulb())
 