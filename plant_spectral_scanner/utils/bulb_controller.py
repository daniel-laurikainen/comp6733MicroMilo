import asyncio
import yaml
from pywizlight import wizlight, PilotBuilder
from typing import Dict

class BulbController:
    def __init__(self, config_path="plant_spectral_scanner/config/bulbs.yaml"):
        self.bulbs = {}  # type: Dict[str, wizlight]
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._load_bulbs(config_path)

    def _load_bulbs(self, config_path):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        for bulb_info in config.get("bulbs", []):
            name = bulb_info.get("name")
            ip = bulb_info.get("ip")
            if name and ip:
                self.bulbs[name] = wizlight(ip)
            else:
                print(f"[WARNING] Bulb entry missing name or ip: {bulb_info}")

    def turn_on_light(self, position: str, hex_color: str):
        """
        Turn on the bulb at 'position' with the given hex_color (e.g. '#FF0000').
        This method runs the asyncio call internally.
        """
        position_key = f"{position}"
        bulb = self.bulbs.get(position_key)
        if not bulb:
            print(f"[ERROR] No bulb found for position '{position}'")
            return
        
        rgb = self._hex_to_rgb(hex_color)
        self.loop.run_until_complete(self._async_turn_on(bulb, rgb))

    def turn_off_all_lights(self):
        """
        Turn off all bulbs asynchronously.
        """
        tasks = [self._async_turn_off(bulb) for bulb in self.bulbs.values()]
        self.loop.run_until_complete(asyncio.gather(*tasks))

    async def _async_turn_on(self, bulb, rgb):
        pilot = PilotBuilder(rgb=rgb, brightness=255)
        await bulb.turn_on(pilot)

    async def _async_turn_off(self, bulb):
        await bulb.turn_off()

    @staticmethod
    def _hex_to_rgb(hex_color: str):
        """Convert hex color string (#RRGGBB) to an RGB tuple."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) != 6:
            raise ValueError(f"Invalid hex color: {hex_color}")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)
