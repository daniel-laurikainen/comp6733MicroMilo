from glob import glob
import csv

def load_latest_baseline() -> dict:
    """
    Load the most recent baseline CSV file from data/baseline/

    Returns:
        Dict: (colour, position) -> sensor -> channel -> value
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
            colour = row.get("colour", "").lower()
            position = row.get("position", "").lower()
            sensor = row["sensor"]
            
            key = (colour, position)
            if key not in baseline_data:
                baseline_data[key] = {}
            
            channels = {
                k: float(v) for k, v in row.items()
                if k.startswith("channel_")
            }
            baseline_data[key][sensor] = channels

    print(f"[INFO] Loaded baseline from: {latest_file}")
    return baseline_data


def subtract_baseline(scan_data: dict, baseline_data: dict, colour: str, position: str) -> dict:
    """
    Subtract baseline from scan data for a specific colour and position.

    Args:
        scan_data: sensor -> channel -> value
        baseline_data: (colour, position) -> sensor -> channel -> value
        colour: the colour of the light used in the scan
        position: the position of the light (e.g. close, middle, far)

    Returns:
        Dict: sensor -> adjusted channel values
    """
    adjusted_data = {}
    key = (colour.lower(), position.lower())

    if key not in baseline_data:
        print(f"[WARNING] No baseline found for ({colour}, {position}). Using zeros.")
        baseline_for_key = {}
    else:
        baseline_for_key = baseline_data[key]

    for sensor in scan_data:
        adjusted_data[sensor] = {}
        for channel in scan_data[sensor]:
            scan_val = scan_data[sensor][channel]
            base_val = baseline_for_key.get(sensor, {}).get(channel, 0)
            adjusted_value = max(scan_val - base_val, 0)
            adjusted_data[sensor][channel] = adjusted_value

    return adjusted_data
