#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility functions for serial communication setup
Date: 2025-07-30
Author: Daniel L.
"""

import os
import yaml
import serial.tools.list_ports

# Load YAML config
def load_sensor_config(config_path="plant_spectral_scanner/config/sensor_ports.yaml"):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)

# Load once at module level
SENSOR_PORT_MAP = load_sensor_config()

def get_sensor_port(sensor_name):
    """
    Get the serial port path for a given sensor name.

    Args:
        sensor_name (str): e.g., 'red_middle_sensor'

    Returns:
        str: Serial port path, or None if not found
    """
    return SENSOR_PORT_MAP.get(sensor_name)

def list_available_ports():
    """
    List all currently available serial ports on the system.

    Returns:
        list of str: Port device names
    """
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

def check_all_ports_connected():
    """
    Check if all expected ports from config are currently connected.

    Returns:
        dict: {sensor_name: True/False}
    """
    available_ports = list_available_ports()
    return {
        name: port in available_ports
        for name, port in SENSOR_PORT_MAP.items()
    }
