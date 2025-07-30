import asyncio
from pywizlight import wizlight, PilotBuilder, discovery


# B8:A8:25:FE:9A:55
 
class BulbController:
    def __init__(self, broadcast_ip="192.168.1.255"):
        self.broadcast_ip = broadcast_ip
        self.bulbs = []

    async def discover_bulbs(self):
        self.bulbs = await discovery.discover_lights(broadcast_space=self.broadcast_ip)
        print(f"Discovered {len(self.bulbs)} bulbs.")
        for i, bulb in enumerate(self.bulbs):
            print(f"Bulb {i}: IP {bulb.ip}")

    async def turn_on_all(self, brightness=255):
        if not self.bulbs:
            await self.discover_bulbs()
        await asyncio.gather(*[bulb.turn_on(PilotBuilder(brightness=brightness)) for bulb in self.bulbs])
        print("All bulbs turned ON")

    async def turn_off_all(self):
        if not self.bulbs:
            await self.discover_bulbs()
        await asyncio.gather(*[bulb.turn_off() for bulb in self.bulbs])
        print("All bulbs turned OFF")

    async def set_color(self, rgb_tuple):
        if not self.bulbs:
            await self.discover_bulbs()
        await asyncio.gather(*[bulb.turn_on(PilotBuilder(rgb=rgb_tuple)) for bulb in self.bulbs])
        print(f"All bulbs set to color {rgb_tuple}")


async def test_bulbs():
    controller = BulbController()

    # Discover bulbs on your network
    await controller.discover_bulbs()

    # Turn all bulbs on at full brightness
    await controller.turn_on_all(brightness=255)

    # Wait 3 seconds so you can see bulbs ON
    await asyncio.sleep(3)

    # Change color to soft blue (example RGB)
    await controller.set_color((0, 0, 255))

    # Wait 3 seconds so you can see the color change
    await asyncio.sleep(3)

    # Turn all bulbs off
    await controller.turn_off_all()

if __name__ == "__main__":
    asyncio.run(test_bulbs())