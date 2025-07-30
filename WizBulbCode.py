#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Control WiZ RGB bulbs: discovery, calibration, and spectral data collection.
Author: Daniel L.
Date: 2025-07-28
"""

import asyncio
import json
import os
from pywizlight import wizlight, PilotBuilder, discovery

# Path to store bulb order
BULB_ORDER_FILE = "wiz_bulb_order.json"

async def calibrate_bulbs(bulbs):
    print("Starting calibration...")

    bulb_order = []
    for i, bulb in enumerate(bulbs):
        print(f"\nIdentifying Bulb #{i + 1} at {bulb.ip}")
        await bulb.turn_on(PilotBuilder(rgb=(255, 0, 0), brightness=255))  # Red
        input(f"Is this bulb #{i + 1}? Press Enter if yes, Ctrl+C to abort.")
        await bulb.turn_off()
        bulb_order.append(bulb.ip)

    with open(BULB_ORDER_FILE, "w") as f:
        json.dump(bulb_order, f)

    print(f"Calibration complete. Order saved to {BULB_ORDER_FILE}")
    return bulb_order

async def load_bulb_order():
    if not os.path.exists(BULB_ORDER_FILE):
        return None
    with open(BULB_ORDER_FILE, "r") as f:
        return json.load(f)

async def collect_spectral_data_with_bulbs(bulbs):
    for idx, bulb in enumerate(bulbs):
        print(f"\nTurning on bulb #{idx + 1} ({bulb.ip}) for spectral measurement...")
        await bulb.turn_on(PilotBuilder(rgb=(255, 255, 255), brightness=255))  # White light
        await asyncio.sleep(2)  # wait for bulb to stabilize
        print(f"Collecting spectral data for bulb #{idx + 1}...")
        # TODO: Replace with your actual spectral measurement function
        collect_spectral_data(idx + 1)
        await bulb.turn_off()

def collect_spectral_data(bulb_number):
    # Placeholder for your actual spectral reading logic
    print(f"[Simulated] Spectral data collected from bulb #{bulb_number}")

async def main():
    print("Discovering WiZ bulbs on network...")
    bulbs = await discovery.discover_lights(broadcast_space="192.168.1.255")

    if not bulbs:
        print("No bulbs found. Make sure they are powered and connected.")
        return

    print(f"Discovered {len(bulbs)} bulbs.")
    for i, bulb in enumerate(bulbs):
        print(f"  Bulb #{i+1}: {bulb.ip}")

    bulb_ips = await load_bulb_order()
    if bulb_ips is None:
        user_input = input("No saved bulb order. Calibrate now? (y/n): ")
        if user_input.lower() == "y":
            bulb_ips = await calibrate_bulbs(bulbs)
        else:
            print("Cannot proceed without bulb order. Exiting.")
            return

    # Recreate bulb objects in calibrated order
    ordered_bulbs = [wizlight(ip) for ip in bulb_ips]

    await collect_spectral_data_with_bulbs(ordered_bulbs)

if __name__ == "__main__":
    asyncio.run(main())
