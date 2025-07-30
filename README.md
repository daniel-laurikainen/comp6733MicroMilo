# Micro Milo – Reflectance-Based Plant Health Monitoring

Micro Milo is a low-cost, RGB reflectance-based plant health monitoring system that detects early signs of stress in plant leaves. Designed with affordability, deployability, and scalability in mind, it bridges the gap between manual inspection and expensive imaging systems like RGB/IR cameras.

## Problem Statement

Current plant monitoring systems either rely on expensive imaging or environmental sensors that don't directly measure the plant’s internal health. Micro Milo introduces a reflectance-based system using RGB light to measure how a plant reflects different wavelengths—providing insights into its physiological condition.

## Project Goals

- Detect early plant stress using RGB reflectance data.
- Build a prototype using accessible, low-cost hardware.
- Develop a data pipeline for real-time analysis and classification using machine learning.
- Explore actuation systems (e.g., auto-watering, alerts) as optional bonus features.

## Key Innovations

- Use of RGB light reflectance for direct non-invasive sensing of leaf health.
- Low-cost, scalable hardware setup.
- Modular design for indoor gardening, greenhouses, or smart farming systems.
- Integration with machine learning for real-time analysis.

## Hardware Components

| Part                                       | Purpose                                  | Qty |
|--------------------------------------------|------------------------------------------|-----|
| Arduino Nano                               | Microcontroller for control and logging  | 1   |
| SparkFun Triad Spectroscopy Sensor AS7265x | Detect reflected light across 18 channels| 5   |
| WIZ E14 Smart Filament Candle              | Controlled RGB light source              | 2   |
| Black 50L Storage Container                | Light-isolated enclosure                 | 2   |
| E14 Cable Cord with On/Off Switch          | Power delivery for smart bulb            | 2   |
| Saddle Clamps + Zip Ties                   | Sensor, LED, and leaf fixture            | N/A |
| Fresh Leaf Samples                         | Test medium                              | N/A |

## System Overview

1. Reflectance Chamber – A sealed, dark enclosure blocks ambient light for controlled measurements.
2. Illumination – RGB light (via WIZ E14 smart bulb) shines on the leaf.
3. Sensing – The AS7265x sensor captures reflected light values across visible and NIR bands.
4. Data Logging – Arduino collects sensor data and sends it to a laptop.
5. Analysis – Python scripts perform statistical and ML analysis (SVM, KNN).
6. Optional Actuation – Automated watering or alerts based on thresholds.

## Data Pipeline

- Serial data from Arduino is streamed to a Python backend.
- CSV files are logged for historical tracking.
- Live graphs show multispectral values and derived indices.

## Data Analysis

In this version of the prototype, we use simple statistical methods and threshold-based comparisons to assess plant health conditions. 

- Time-series plots of reflectance data are used to observe trends and deviations over time.
- Band ratios (e.g., red/green, red/blue) and simple vegetation indices (e.g., Green-Red Vegetation Index) help highlight changes associated with stress.
- Reflected light intensities are compared against baseline healthy values to detect potential signs of drought or disease.
- Histograms and average reflectance values can help differentiate healthy versus stressed leaf states.

These techniques provide a foundation for future integration of machine learning models once more data has been collected.


## Future Extensions

- Alerts via email or Telegram.
- Scaling to monitor whole plants or plant groups.
- Deeper time-series pattern detection using neural networks.

## Scope & Limitations

- Limited to sensing one plant at a time.
- Works in controlled lighting only (indoor environment).
- No power harvesting or wireless communication in MVP.
- Basic statistical/ML models (no deep learning yet).

## Project Timeline

| Milestone                      | Weeks | Highlights                                                                 |
|-------------------------------|-------|---------------------------------------------------------------------------|
| Requirements & Procurement    | 1–5   | Scope finalized, hardware ordered                                        |
| Assembly & Calibration        | 5–6   | Enclosure build, LED/sensor calibration                                  |
| Data Collection & Analysis    | 7     | Healthy vs stressed data logging, ML pipeline setup                      |
| Stress Testing & Validation   | 8     | Disease/drought simulation, daily logs, safety checks                    |
| Bonus Features                | 8     | Notifications, extended sensing                                          |
| Integration & Demo            | 9–10  | Final build, user guide, performance demo                                |

## References

1. Chen et al. (2020). *Skewed distribution of leaf colour RGB model*. [Plant Methods](https://doi.org/10.1186/s13007-020-0561-2).
2. Péter Bodor-Pesti et al. (2025). *LeafLaminaMap: Exploring RGB Colour Indices*. [AgriEngineering](https://doi.org/10.3390/agriengineering7020039).
3. Mir et al. (2022). *RGB LED bulbs for communication, harvesting and sensing*. IEEE PerCom.
4. Science Buddies. (2015). [TCS3200 Sensor Tutorial](https://www.sciencebuddies.org/science-fair-projects/project-ideas/Elec_p110/electricity-electronics/leaf-color-detection).

## Setup Instructions

> Full instructions and diagrams coming soon.

1. Connect AS7265x to Arduino Nano via Qwiic/I2C.
2. Set up the WIZ smart bulb in the container.
3. Upload Arduino firmware from `/firmware` folder.
4. Run Python scripts in `/scripts` to collect and analyse data.

## Repository Structure

```bash
micro-milo/
├── firmware/                 # Arduino code
├── scripts/                  # Python data processing + ML scripts
├── data/                     # Collected CSV data
├── hardware/                 # Schematics, wiring diagrams
├── docs/                     # Project report, proposal, references
├── plant_spectral_scanner/  # Bulb control logic and spectral data interface
├── README.md                 # Main project overview
