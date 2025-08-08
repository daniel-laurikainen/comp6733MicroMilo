#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sensor controller for AS7265x devices

Created on: 2025-07-30
Author: Daniel L.
"""

import serial
import yaml
import time
from typing import Dict

wavelengths = [410, 435, 460, 485, 510, 535, 560, 585, 610, 645, 680, 705, 730, 760, 810, 890, 900, 940]

class SensorController:
    def __init__(self, config_path: str = 'plant_spectral_scanner/config/sensor_ports.yaml'):
        """
        Initializes sensor controller and loads sensor-port mapping
        """
        self.sensors: Dict[str, serial.Serial] = {}
        self.ports = self.load_ports(config_path)

    def load_ports(self, config_path: str) -> Dict[str, str]:
        """
        Load sensor-port mapping from YAML file
        """
        with open(config_path, 'r') as f:
            ports = yaml.safe_load(f)
        return ports

    def connect_sensors(self):
        """
        Connect to all sensors via serial
        """
        for name, port in self.ports.items():
            try:
                self.sensors[name] = serial.Serial(port, baudrate=9600, timeout=2)
                print(f"[CONNECTED] {name} on {port}")
                time.sleep(2)  # Allow time for serial to stabilize
            except Exception as e:
                print(f"[ERROR] Could not connect to {name} on {port}: {e}")

    def disconnect_sensors(self):
        """
        Close all serial connections
        """
        for name, ser in self.sensors.items():
            ser.close()
            print(f"[DISCONNECTED] {name}")

    def read_sensor(self, name: str) -> Dict[str, float]:
        """
        Simulate reading data from a sensor. Replace this with real logic.
        """
        ser = self.sensors.get(name)
        if ser is None:
            print(f"[ERROR] Sensor {name} not connected.")
            return {}

        try:
            # Simulated read request
            ser.write(b'READ_DATA\n')  # This depends on your actual sensor protocol
            line = ser.readline().decode('utf-8').strip()
            # Example: Parse comma-separated values like "123,456,..."
            values = list(map(float, line.split(',')))
            return {f"channel_{i+1}_{wavelengths[i]}": val for i, val in enumerate(values)}
        except Exception as e:
            print(f"[ERROR] Failed to read from {name}: {e}")
            return {}

    def read_all_sensors(self) -> Dict[str, Dict[str, float]]:
        """
        Read spectral data from all connected sensors
        """
        if not self.sensors:
            print("[WARNING] No sensors are connected.")
            return {}

        data = {}
        for name in self.sensors:
            data[name] = self.read_sensor(name)
        return data
