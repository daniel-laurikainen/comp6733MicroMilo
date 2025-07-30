#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script for interacting with AS7265x sensors with baseline subtraction

Created on: 2025-07-30
Author: Daniel L.
"""

import os
import csv
import time
from datetime import datetime
from glob import glob
from utils.sensor_controller import SensorController  # fixed import


def prompt_mode() -> str:
    """
    Prompt the user to select scan, baseline, or quit mode
    """
    while True:
        print("\nSelect mode:")
        print("[1] Scan")
        print("[2] Baseline")
        print("[3] Quit")
        choice = input("Enter 1, 2 or 3: ").strip()
        if choice == '1':
            return "scan"
        elif choice == '2':
            return "baseline"
        elif choice == '3':
            return "quit"
        else:
            print("Invalid input. Please enter 1, 2 or 3.")


def save_to_csv(data: dict, mode: str, description: str = "", adjusted: bool = False) -> None:
    """
    Save sensor data to a CSV file

    Args:
        data: Dictionary of sensor -> channel -> value
        mode: "scan" or "baseline"
        description: Description of scanned object (used only in scan mode)
        adjusted: Whether the scan data is baseline-adjusted
    """
    folder_name = "scans" if mode == "scan" else "baseline"
    base_dir = os.path.join("data", folder_name)
    os.makedirs(base_dir, exist_ok=True)

    timestamp_now = datetime.now()
    timestamp_str = timestamp_now.strftime('%Y%m%d_%H%M%S')
    filename = f"{'adjusted_' if adjusted else ''}{mode}_{timestamp_str}.csv"
    filepath = os.path.join(base_dir, filename)

    with open(filepath, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Compose header
        header = ["timestamp"]
        if mode == "scan":
            header.append("description")
        header.append("sensor")
        header.extend([f"channel_{i+1}" for i in range(len(next(iter(data.values()))))])
        writer.writerow(header)

        # Write each sensor's row
        for sensor, channels in data.items():
            row = [timestamp_now.strftime('%Y-%m-%d %H:%M:%S')]
            if mode == "scan":
                row.append(description)
            row.append(sensor)
            row.extend(channels.values())
            writer.writerow(row)

    print(f"[SAVED] {mode.capitalize()} data saved to {filepath}")


def load_latest_baseline() -> dict:
    """
    Load the most recent baseline CSV file from data/baseline/

    Returns:
        Dict: sensor -> channel -> value
    """
    baseline_files = sorted(glob("data/baseline/baseline_*.csv"), reverse=True)
    if not baseline_files:
        print("[ERROR] No baseline found. Please create a baseline first.")
        return None

    latest_file = baseline_files[0]
    baseline_data = {}

    with open(latest_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sensor = row["sensor"]
            channels = {f"channel_{i+1}": float(row[f"channel_{i+1}"]) for i in range(len(row) - 3)}
            baseline_data[sensor] = channels

    print(f"[INFO] Loaded baseline from: {latest_file}")
    return baseline_data


def subtract_baseline(scan_data: dict, baseline_data: dict) -> dict:
    """
    Subtract baseline from scan data

    Returns:
        Dict: sensor -> adjusted channel values
    """
    adjusted_data = {}
    for sensor in scan_data:
        adjusted_data[sensor] = {}
        for channel in scan_data[sensor]:
            scan_val = scan_data[sensor][channel]
            base_val = baseline_data.get(sensor, {}).get(channel, 0)
            adjusted_value = max(scan_val - base_val, 0)
            adjusted_data[sensor][channel] = adjusted_value
    return adjusted_data


def main():
    controller = SensorController()
    controller.connect_sensors()

    print("[READY] Sensors connected. Waiting for instructions...")

    try:
        while True:
            mode = prompt_mode()

            if mode == "quit":
                print("[EXITING] Ending session.")
                break

            description = ""
            if mode == "scan":
                description = input("Enter a description for the object being scanned: ").strip()

            print(f"[INFO] Taking a {mode} measurement...")
            time.sleep(1)

            data = controller.read_all_sensors()

            if mode == "baseline":
                save_to_csv(data, mode)
            elif mode == "scan":
                baseline_data = load_latest_baseline()
                if baseline_data is None:
                    continue  # skip saving if no baseline
                adjusted = subtract_baseline(data, baseline_data)
                save_to_csv(adjusted, mode, description, adjusted=True)

    finally:
        controller.disconnect_sensors()
        print("[DISCONNECTED] Sensors safely disconnected.")


if __name__ == "__main__":
    main()
