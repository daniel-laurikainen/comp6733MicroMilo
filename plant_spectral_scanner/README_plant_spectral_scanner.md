# Plant Spectral Scanner

This folder contains all code related to controlling the spectral scanning system, which includes:

- Light source (bulb) control
- Sensor triggering and data capture
- Integration logic to support baseline scans, adjusted scans, and scan metadata

This module is a critical part of the micro-milo system, enabling automated and repeatable spectral analysis of plant samples under controlled lighting conditions.

---

## Folder Structure

```
plant_spectral_scanner/
├── config/
│   ├── bulbs.yaml              # Bulb IP addresses and settings
│   └── sensor_ports.yaml       # Sensor port configurations
├── data/                       # Output directory for scan data
├── scripts/
│   ├── baseline_utils.py       # Baseline scan utilities
│   ├── csv_utils.py           # CSV file handling
│   └── prompt_mode.py         # Interactive prompt interface
├── utils/
│   ├── bulb_controller.py     # Controls smart bulbs via IP
│   ├── sensor_controller.py   # Manages AS7265x sensor communication
│   └── serial_utils.py        # Serial communication utilities
├── main.py                    # Main application entry point
└── test.py                    # Testing and validation scripts
```

---

## Key Features

- 🔦 **Multi-bulb Support**: Controls multiple WiZ smart bulbs at different positions
- 📊 **Scan Modes**: Supports both scan and baseline modes with metadata tagging
- 🕓 **Timestamped Logging**: Saves readings with precise timestamps
- 🧪 **Interactive Mode**: Prompt-based interface for easy operation

---

## Quick Start

### 1. Configure System
Edit configuration files in the `config/` directory:

**bulbs.yaml:**
```yaml
bulbs:
  - name: bulb_close
    ip: 192.168.119.60
  - name: bulb_middle
    ip: 192.168.119.238
  - name: bulb_far
    ip: 192.168.119.176
```

**sensor_ports.yaml:**
```yaml
sensor:
  port_name: /dev/cu.portnumber 
```

### 2. Run Scanner
```bash
python main.py
```

### 3. Output Location
Scan data is saved to the `data/` folder with automatic timestamp-based filenames.

---

## Dependencies

Install required packages:
```bash
pip install pywizlight pyserial pyyaml
```

---

## Example Output

CSV files include timestamp, metadata, and 18-channel spectral data:
```csv
timestamp,description,colour,position,sensor,channel_1,...,channel_18
2025-07-30 15:30:15,leaf sample,blue,close,sensor_1,123,...,28
```

---

## Usage Modes

- **Interactive Mode**: Run `python main.py` for guided prompts
- **Baseline Capture**: Use baseline utilities in `scripts/baseline_utils.py`
- **Batch Processing**: Customize `main.py` for automated scanning

---

## Troubleshooting

- **Bulb Issues**: Check IP addresses in `config/bulbs.yaml`
- **Sensor Issues**: Verify port settings in `config/sensor_ports.yaml`
- **Permission Errors**: Ensure write access to `data/` directory

---

## Next Steps

- [ ] Improve error handling for hardware failures
- [ ] Add CLI arguments for configuration
- [ ] Integrate with full-system automation