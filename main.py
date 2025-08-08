#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script for interacting with AS7265x sensors with baseline subtraction

Created on: 2025-07-30
Author: Daniel L.
"""

import os
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

import pickle
import pandas as pd

def check_basil_health(model_path: str, csv_path: str) -> str:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    df = pd.read_csv(csv_path)
    X = df.drop(columns=["timestamp", "description", "bulb_colour", "bulb_position", "sensor_position"], errors="ignore")
    prediction = model.predict(X.mean().to_frame().T)
    return "Healthy" if prediction[0] == 1 else "Unhealthy"

def check_leaf_health(model_path: str, csv_path: str) -> str:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    df = pd.read_csv(csv_path)
    X = df.drop(columns=["timestamp", "description", "bulb_colour", "bulb_position", "sensor_position"], errors="ignore")
    prediction = model.predict(X.mean().to_frame().T)
    return "Healthy" if prediction[0] == 1 else "Unhealthy"

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
            scan_type = None  # "leaf" or "basil"

            if mode == "scan":
                # Ask for scan type before baseline load
                while True:
                    scan_type_input = input("Scan type? Enter 'leaf' or 'basil': ").strip().lower()
                    if scan_type_input in ["leaf", "basil"]:
                        scan_type = scan_type_input
                        break
                    print("[ERROR] Please enter 'leaf' or 'basil'.")
                
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
                        subfolder = os.path.join("scans", f"{scan_type}_scans")
                        current_filename = save_to_csv(
                            data=data_baselined,
                            mode=mode,
                            description=description,
                            colour=colour,
                            position=position,
                            adjusted=True,
                            filename=current_filename,
                            extra_subfolder=subfolder
                        )
            if current_filename:
                print(f"[COMPLETE] {mode.capitalize()} data successfully saved to '{current_filename}'")

                # === Post-scan health check ===
                if mode == "scan":
                    model_choice = None
                    if scan_type == "basil":
                        model_choice = "basil_model.pkl"
                        check_func = check_basil_health
                    elif scan_type == "leaf":
                        model_choice = "leaf_model.pkl"
                        check_func = check_leaf_health

                    run_check = input(f"Do you want to check {scan_type} health? (y/n): ").strip().lower()
                    if run_check == "y":
                        base_project_dir = os.path.dirname(os.path.abspath(__file__))  # where main.py is
                        model_path = os.path.join(base_project_dir, "data_processing", model_choice)
                        scan_path = os.path.join(
                            base_project_dir,
                            "data",
                            "scans",
                            f"{scan_type}_scans",
                            current_filename
                        )
                        if os.path.exists(model_path) and os.path.exists(scan_path):
                            print(f"[HEALTH CHECK] Loading {scan_type} model from {model_path}")
                            result = check_func(model_path, scan_path)
                            print(f"[RESULT] {scan_type.capitalize()} health: {result}")
                        else:
                            print("[ERROR] Model file or scan data not found.")
            

    finally:
        sensor_controller.disconnect_sensors()
        bulb_controller.turn_off_all_lights()
        print("[DISCONNECTED] Sensors safely disconnected.")


if __name__ == "__main__":
    main()
