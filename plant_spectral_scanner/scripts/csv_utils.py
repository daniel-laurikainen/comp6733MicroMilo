import os
import csv
from datetime import datetime



def save_to_csv(data: dict, mode: str, description: str = "", adjusted: bool = False,
                colour: str = "", position: str = "", filename: str = "") -> str:
    """
    Save sensor data to a CSV file. If filename is provided, appends to existing file.

    Args:
        data: Dictionary of sensor -> channel -> value
        mode: "scan" or "baseline"
        description: Description of scanned object (used only in scan mode)
        adjusted: Whether the scan data is baseline-adjusted
        colour: Light colour used (e.g. red, green, blue, white)
        position: Light source position (e.g. close, middle, far)
        filename: Optional filename to write to (for grouping multiple scan entries)

    Returns:
        The full filepath where the data was saved
    """

    wavelengths = [410, 435, 460, 485, 510, 535, 560, 585, 610, 645, 680, 705, 730, 760, 810, 890, 900, 940]

    # Get the base directory: parent of plant_spectral_scanner/
    base_project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    folder_name = "scans" if mode == "scan" else "baseline"
    data_dir = os.path.join(base_project_dir, "data", folder_name)
    os.makedirs(data_dir, exist_ok=True)

    # Generate filename only once per full scan session
    if not filename:
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{description + '_' if adjusted else ''}{mode}_{timestamp_str}.csv"

    filepath = os.path.join(data_dir, filename)
    file_exists = os.path.exists(filepath)

    with open(filepath, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header only once
        if not file_exists:
            header = ["timestamp"]
            if mode == "scan":
                header.append("description")
            header.extend(["bulb_colour", "bulb_position", "sensor_position"])
            header.extend([f"channel_{i+1}_{wl}" for i, wl in enumerate(wavelengths)])
            writer.writerow(header)

        timestamp_now = datetime.now()
        # Write each sensor's row
        for sensor, channels in data.items():
            row = [timestamp_now.strftime('%Y-%m-%d %H:%M:%S')]
            if mode == "scan":
                row.append(description)
            row.extend([colour, position, sensor])
            row.extend(channels.values())
            writer.writerow(row)

    return filename