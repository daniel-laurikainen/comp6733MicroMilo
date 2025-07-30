# Data Storage Guidelines for AS7265x Sensor Project

This document describes how the spectral data collected from the AS7265x sensor should be stored for consistency and ease of analysis.

1. Data Format:
   - Data should be stored in CSV (Comma-Separated Values) format.
   - Each row represents one timestamped reading of all spectral channels.

2. File Structure:
- The first row must be the **CSV header**, which includes:
  - A timestamp
  - (Optional) A description of the object being scanned (for scan mode only)
  - Light `colour` and `position`
  - The `sensor` identifier
  - 18 channel values labeled as `channel_1` through `channel_18`
- Each subsequent row contains the recorded values for a single sensor reading.

3. Recommended CSV Header:
   timestamp,410nm,435nm,460nm,485nm,510nm,535nm,560nm,585nm,610nm,645nm,680nm,705nm,730nm,760nm,810nm,860nm,900nm,940nm

4. Timestamp:
   - Use the format: YYYY-MM-DD HH:MM:SS (e.g., 2025-07-17 10:15:30).
   - Represents the exact time when the measurement was taken.

5. Spectral Channels:
   - Values correspond to sensor readings at specified wavelengths in nanometers.
   - All 18 channels should be included in the order shown in the header.

6. Example CSV Row:
   2025-07-17 10:15:30,123,110,115,100,95,80,90,85,75,60,70,65,50,55,45,40,35,30

7. Storage Location:
   - Store data files in the `data/` directory of the project.
   - Use descriptive filenames including date/time (e.g., `spectral_data_20250717.csv`).

8. Additional Notes:
   - Append new data to existing files for continuous logging.
   - Ensure data integrity by validating sensor readings before saving.
   - Backup data regularly to avoid loss.

---

Following these guidelines will ensure that your spectral data is well-organized, easy to parse, and ready for analysis or visualization.

