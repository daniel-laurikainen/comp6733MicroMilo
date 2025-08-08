#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script for interacting with AS7265x sensors with baseline subtraction

Created on: 2025-07-30
Author: Daniel L.
"""

import time
from plant_spectral_scanner.utils.sensor_controller import SensorController
from plant_spectral_scanner.utils.bulb_controller import BulbController

from plant_spectral_scanner.scripts.prompt_mode import prompt_mode
from plant_spectral_scanner.scripts.csv_utils import save_to_csv
from plant_spectral_scanner.scripts.baseline_utils import load_latest_baseline, subtract_baseline


# === Global timing variables ===
BULB_STABILIZE_TIME = 1.50     # seconds to wait after turning bulb on to stabilize
BULB_OFF_DELAY = 0.5          # seconds to wait after turning bulb off before next step
MODE_START_DELAY = 1.0        # seconds to wait after starting mode before measurement

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
    bulb_positions = ["close_bulb", "middle_bulb", "far_bulb"]

    try:
        while True:
            mode = prompt_mode()
            bulb_controller.turn_off_all_lights()

            if mode == "quit":
                print("[EXITING] Ending session.")
                break

            baseline_data = None
            current_filename = None

            if mode == "scan":
                baseline_data = load_latest_baseline()
                if baseline_data is None:
                    continue
            
            description = ""
            if mode == "scan":
                description = input("Enter a description for the object being scanned: ").strip()

            print(f"[INFO] Starting {mode} measurements...")
            time.sleep(MODE_START_DELAY)


            for colour, hex_code in colours.items():
                print(f"[{mode.upper()}] Measuring for {colour} light")
                for position in bulb_positions:
                    bulb_controller.turn_on_light(position, hex_code)
                    time.sleep(BULB_STABILIZE_TIME)  # allow light to stabilize

                    data = sensor_controller.read_all_sensors()

                    bulb_controller.turn_off_all_lights()
                    time.sleep(BULB_OFF_DELAY)

                    if mode == "baseline":
                        current_filename = save_to_csv(
                            data=data,
                            mode=mode,
                            colour=colour,
                            position=position,
                            filename=current_filename
                        )
                    elif mode == "scan":
                        data_baselined = subtract_baseline(data, baseline_data, colour, position)
                        current_filename = save_to_csv(
                            data=data_baselined,
                            mode=mode,
                            description=description,
                            colour=colour,
                            position=position,
                            adjusted=True,
                            filename=current_filename
                        )
            if current_filename:
                print(f"[COMPLETE] {mode.capitalize()} data successfully saved to '{current_filename}'")
    finally:
        sensor_controller.disconnect_sensors()
        bulb_controller.turn_off_all_lights()
        print("[DISCONNECTED] Sensors safely disconnected.")


if __name__ == "__main__":
    main()
