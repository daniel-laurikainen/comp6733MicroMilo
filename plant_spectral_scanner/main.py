#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script for interacting with AS7265x sensors with baseline subtraction

Created on: 2025-07-30
Author: Daniel L.
"""

import time
from utils.sensor_controller import SensorController
from utils.bulb_controller import BulbController

from scripts.prompt_mode import prompt_mode
from scripts.csv_utils import save_to_csv
from scripts.baseline_utils import load_latest_baseline, subtract_baseline

def main():
    sensor_controller = SensorController()
    sensor_controller.connect_sensors()

    bulb_controller = BulbController()

    print("[READY] Sensors connected. Waiting for instructions...")

    colours = {
        "Red": "#FF0000",
        "Green": "#00FF00",
        "Blue": "#0000FF",
        "White": "#FFFFFF"
    }
    bulb_positions = ["close", "middle", "far"]

    try:
        while True:
            mode = prompt_mode()
            bulb_controller.turn_off_all_lights()

            if mode == "quit":
                print("[EXITING] Ending session.")
                break

            description = ""
            if mode == "scan":
                description = input("Enter a description for the object being scanned: ").strip()

            print(f"[INFO] Starting {mode} measurements...")
            time.sleep(1)

            baseline_data = None
            if mode == "scan":
                baseline_data = load_latest_baseline()
                if baseline_data is None:
                    print("[ERROR] No baseline data available. Skipping scan.")
                    continue

            for colour, hex_code in colours.items():
                for position in bulb_positions:
                    print(f"[{mode.upper()}] Measuring for {colour} light at {position} position...")
                    bulb_controller.turn_on_light(position, hex_code)
                    time.sleep(2)  # allow light to stabilize

                    data = sensor_controller.read_all_sensors()

                    bulb_controller.turn_off_light()
                    time.sleep(0.5)

                    if mode == "baseline":
                        save_to_csv(data, mode, colour=colour, position=position)
                    elif mode == "scan":
                        adjusted = subtract_baseline(data, baseline_data, colour, position)
                        save_to_csv(adjusted, mode, description, colour, position, adjusted=True)

    finally:
        sensor_controller.disconnect_sensors()
        bulb_controller.turn_off_all_lights()
        print("[DISCONNECTED] Sensors safely disconnected.")


if __name__ == "__main__":
    main()
