import os
import csv
from datetime import datetime

def save_to_csv(data: dict, mode: str, description: str = "", adjusted: bool = False, colour: str = "", position: str = "") -> None:
    """
    Save sensor data to a CSV file

    Args:
        data: Dictionary of sensor -> channel -> value
        mode: "scan" or "baseline"
        description: Description of scanned object (used only in scan mode)
        adjusted: Whether the scan data is baseline-adjusted
        colour: Light colour used (e.g. red, green, blue, white)
        position: Light source position (e.g. close, middle, far)
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
        header.extend(["colour", "position", "sensor"])
        header.extend([f"channel_{i+1}" for i in range(len(next(iter(data.values()))))])
        writer.writerow(header)

        # Write each sensor's row
        for sensor, channels in data.items():
            row = [timestamp_now.strftime('%Y-%m-%d %H:%M:%S')]
            if mode == "scan":
                row.append(description)
            row.extend([colour, position, sensor])
            row.extend(channels.values())
            writer.writerow(row)

    print(f"[SAVED] {mode.capitalize()} data saved to {filepath}")
