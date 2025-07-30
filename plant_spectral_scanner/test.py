import asyncio
from pywizlight import wizlight, PilotBuilder

async def toggle_bulb():
    bulb = wizlight("192.168.119.238")  # Replace with your bulb's IP

    colors = {
        "red": (255, 0, 0),
        "green": (0, 255, 0),
        "blue": (0, 0, 255),
        "white": (255, 255, 255)
    }

    for color_name, rgb in colors.items():
        print(f"Turning bulb ON with {color_name}...")
        # Set RGB color with full brightness (255)
        await bulb.turn_on(PilotBuilder(rgb=rgb, brightness=255))
        print(f"Bulb is {color_name}")
        await asyncio.sleep(3)  # Wait 3 seconds

        print("Turning bulb OFF...")
        await bulb.turn_off()
        await asyncio.sleep(1)  # Small delay before next color

if __name__ == "__main__":
    asyncio.run(toggle_bulb())

 

# bulb 1 192.168.119.60
# bulb 2 192.168.119.238
# bulb 3 192.168.119.176