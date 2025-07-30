import serial
import serial.tools.list_ports
import time
import csv
import os
from datetime import datetime
from typing import List, Dict, Optional

class AS7265xController:
    def __init__(self, baudrate: int = 9600):
        """
        Initialize the AS7265x controller for multiple sensors
        
        Args:
            baudrate: Communication speed (default 9600)
        """
        self.baudrate = baudrate
        self.sensors = {}  # Dictionary to store sensor connections
        self.sensor_order = []  # Order of sensors as determined by user
        
        # Channel names for AS7265x (18 channels total)
        self.channel_names = [
            'A_410nm', 'B_435nm', 'C_460nm', 'D_485nm', 'E_510nm', 'F_535nm',  # UV channels
            'G_560nm', 'H_585nm', 'R_610nm', 'I_645nm', 'S_680nm', 'J_705nm',  # VIS channels  
            'T_730nm', 'U_760nm', 'V_810nm', 'W_860nm', 'K_900nm', 'L_940nm'   # NIR channels
        ]
    
    def find_arduino_sensors(self) -> Dict[str, str]:
        """Find all Arduino Nano 33 BLE devices with AS7265x sensors"""
        print("🔍 Scanning for Arduino Nano 33 BLE devices with AS7265x sensors...")
        
        found_sensors = {}
        ports = []
        
        # Find all Nano 33 BLE ports
        for port in serial.tools.list_ports.comports():
            if 'nano' in port.description.lower() or 'arduino' in port.description.lower():
                ports.append(port.device)
                print(f"   📍 Found Nano 33 BLE: {port.device}")
        
        if not ports:
            print("   ❌ No Nano 33 BLE devices found!")
            return found_sensors
        
        # Test each port for AS7265x sensor code
        for port_name in ports:
            print(f"   🔗 Testing {port_name}...")
            
            try:
                # Connect with longer timeout for Nano 33 BLE
                ser = serial.Serial(port_name, self.baudrate, timeout=5)
                time.sleep(3)  # Wait for initialization
                
                # Clear any startup messages
                ser.flushInput()
                time.sleep(1)
                
                # Test communication
                ser.write(b"PING\n")
                time.sleep(1)
                response = ser.readline().decode().strip()
                
                if "PONG" not in response:
                    ser.close()
                    print(f"   ❌ No valid response from {port_name}")
                    continue
                
                # Test sensor
                ser.write(b"CHECK_SENSOR\n")
                time.sleep(1)
                sensor_response = ser.readline().decode().strip()
                
                if "SENSOR_OK" in sensor_response:
                    # Get sensor ID
                    ser.write(b"GET_ID\n")
                    time.sleep(1)
                    id_response = ser.readline().decode().strip()
                    
                    sensor_id = "Unknown"
                    if id_response.startswith("ID:"):
                        sensor_id = id_response.split(":", 1)[1]
                    
                    found_sensors[sensor_id] = port_name
                    print(f"   ✅ AS7265x sensor found: {sensor_id} on {port_name}")
                else:
                    print(f"   ❌ No AS7265x sensor on {port_name}")
                
                ser.close()
                
            except Exception as e:
                print(f"   ❌ Error testing {port_name}: {e}")
        
        print(f"\n✅ Found {len(found_sensors)} AS7265x sensor(s)")
        return found_sensors
    
    def connect_to_sensors(self, sensors: Dict[str, str]) -> bool:
        """Connect to all found sensors"""
        print("\n🔗 Connecting to sensors...")
        
        self.sensors = {}
        
        for sensor_id, port in sensors.items():
            try:
                print(f"   Connecting to {sensor_id} on {port}...")
                ser = serial.Serial(port, self.baudrate, timeout=5)
                time.sleep(2)
                
                # Test connection
                ser.write(b"PING\n")
                time.sleep(1)
                response = ser.readline().decode().strip()
                
                if "PONG" in response:
                    self.sensors[sensor_id] = ser
                    print(f"   ✅ Connected to {sensor_id}")
                else:
                    ser.close()
                    print(f"   ❌ Failed to connect to {sensor_id}")
                    
            except Exception as e:
                print(f"   ❌ Connection error for {sensor_id}: {e}")
        
        if self.sensors:
            print(f"\n✅ Successfully connected to {len(self.sensors)} sensor(s)")
            return True
        else:
            print("\n❌ Failed to connect to any sensors!")
            return False
    
    def disconnect_all(self):
        """Disconnect from all sensors"""
        for sensor_id, ser in self.sensors.items():
            if ser and ser.is_open:
                try:
                    ser.close()
                    print(f"✅ Disconnected from {sensor_id}")
                except:
                    pass
        self.sensors = {}
    
    def send_command_to_sensor(self, sensor_id: str, command: str, timeout: float = 2.0) -> List[str]:
        """Send command to specific sensor and return response lines"""
        if sensor_id not in self.sensors:
            return [f"ERROR: Sensor {sensor_id} not connected"]
        
        try:
            ser = self.sensors[sensor_id]
            ser.flushInput()
            ser.write(f"{command}\n".encode())
            time.sleep(timeout)
            
            responses = []
            while ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    responses.append(line)
            
            return responses
            
        except Exception as e:
            return [f"ERROR: {e}"]
    
    def phase1_identify_sensors(self):
        """Phase 1: Flash sensors for identification"""
        print("\n🔆 PHASE 1: Sensor Identification")
        print("=" * 60)
        
        if not self.sensors:
            print("❌ No sensors connected!")
            return False
        
        sensor_list = list(self.sensors.keys())
        print(f"Found {len(sensor_list)} sensor(s): {', '.join(sensor_list)}")
        print("\nEach sensor will flash its LEDs 3 times for identification.")
        print("Please observe which physical sensor corresponds to each ID.")
        print("\nPress Enter to start the identification process...")
        input()
        
        for i, sensor_id in enumerate(sensor_list, 1):
            print(f"\n💡 Flashing {sensor_id} ({i}/{len(sensor_list)})")
            print("   Watch for the flashing LEDs on your physical sensor!")
            
            responses = self.send_command_to_sensor(sensor_id, "LED_FLASH", 5.0)
            
            # Monitor the flash sequence
            flash_success = False
            for response in responses:
                if "FLASH_START" in response:
                    print("   🔥 Flashing started...")
                    flash_success = True
                elif "FLASH_ON" in response:
                    flash_num = response.split(":")[-1] if ":" in response else "?"
                    print(f"   💡 Flash {flash_num} - LEDs ON")
                elif "FLASH_OFF" in response:
                    flash_num = response.split(":")[-1] if ":" in response else "?"
                    print(f"   ⚫ Flash {flash_num} - LEDs OFF")
                elif "FLASH_END" in response:
                    print("   ✅ Flashing complete")
            
            if not flash_success:
                print("   ❌ Flash command failed - check sensor connections")
                # Try basic LED control as fallback
                self.send_command_to_sensor(sensor_id, "LED_ON", 1.0)
                time.sleep(2)
                self.send_command_to_sensor(sensor_id, "LED_OFF", 1.0)
            
            if i < len(sensor_list):
                print("   Waiting 3 seconds before next sensor...")
                time.sleep(3)
        
        print("\n✅ Identification phase complete!")
        print("You should have observed which physical sensor corresponds to each ID.")
        return True
    
    def phase2_get_sensor_order(self):
        """Phase 2: Get sensor order from user"""
        print("\n📝 PHASE 2: Sensor Order Input")
        print("=" * 60)
        
        if not self.sensors:
            print("❌ No sensors connected!")
            return False
        
        sensor_list = list(self.sensors.keys())
        print(f"Available sensors: {', '.join(sensor_list)}")
        print("\nBased on the flashing sequence, please enter the order of sensors")
        print("as you want them to appear in your data (e.g., from left to right,")
        print("front to back, etc.).")
        print(f"\nYou can enter:")
        print(f"  • Sensor IDs: {', '.join(sensor_list)}")
        print(f"  • Numbers 1-{len(sensor_list)} (corresponding to the list above)")
        
        while True:
            try:
                user_input = input(f"\nEnter sensor order (comma-separated): ").strip()
                
                if not user_input:
                    print("Please enter the sensor order.")
                    continue
                
                # Parse input
                parts = [part.strip() for part in user_input.split(',')]
                
                # Check if input is numbers or sensor IDs
                if all(part.isdigit() for part in parts):
                    # Numbers provided - convert to sensor IDs
                    try:
                        indices = [int(part) - 1 for part in parts]
                        if all(0 <= idx < len(sensor_list) for idx in indices):
                            self.sensor_order = [sensor_list[idx] for idx in indices]
                        else:
                            print(f"Invalid numbers. Use 1-{len(sensor_list)}")
                            continue
                    except ValueError:
                        print("Invalid number format")
                        continue
                else:
                    # Sensor IDs provided
                    if all(sensor_id in sensor_list for sensor_id in parts):
                        self.sensor_order = parts
                    else:
                        invalid = [s for s in parts if s not in sensor_list]
                        print(f"Invalid sensor IDs: {', '.join(invalid)}")
                        print(f"Available: {', '.join(sensor_list)}")
                        continue
                
                # Validate all sensors included and no duplicates
                if len(set(self.sensor_order)) != len(self.sensor_order):
                    print("Each sensor should appear only once")
                    continue
                
                if len(self.sensor_order) != len(sensor_list):
                    print(f"Please include all {len(sensor_list)} sensors")
                    continue
                
                break
                
            except KeyboardInterrupt:
                print("\nOperation cancelled")
                return False
        
        print(f"\n✅ Sensor order recorded: {' → '.join(self.sensor_order)}")
        
        # Assign friendly names to sensors
        print("\nOptionally, you can assign custom names to your sensors:")
        print("(Press Enter to keep current IDs)")
        
        sensor_names = {}
        for i, sensor_id in enumerate(self.sensor_order, 1):
            custom_name = input(f"Name for sensor {i} ({sensor_id}): ").strip()
            if custom_name:
                sensor_names[sensor_id] = custom_name
                # Update the sensor ID on the Arduino
                self.send_command_to_sensor(sensor_id, f"SET_ID {custom_name}")
            else:
                sensor_names[sensor_id] = sensor_id
        
        # Update sensor order with new names
        self.sensor_order = [sensor_names[sensor_id] for sensor_id in self.sensor_order]
        
        print(f"\n✅ Final sensor order: {' → '.join(self.sensor_order)}")
        return True
    
    def phase3_scan_and_save(self, filename: Optional[str] = None):
        """Phase 3: Scan sensors and save calibrated data to CSV"""
        print("\n📊 PHASE 3: Data Scanning and Saving")
        print("=" * 60)
        
        if not self.sensor_order:
            print("❌ Sensor order not set!")
            return False
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"as7265x_spectral_data_{timestamp}.csv"
        
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        print(f"Data will be saved to: {filename}")
        print(f"Scanning {len(self.sensor_order)} sensors in order: {' → '.join(self.sensor_order)}")
        print("📊 Data type: Calibrated spectral values (factory calibrated)")
        
        # Get scan parameters from user
        while True:
            try:
                num_readings = int(input("\nHow many readings per sensor? (default: 5): ") or "5")
                if num_readings > 0:
                    break
                else:
                    print("Please enter a positive number")
            except ValueError:
                print("Please enter a valid number")
        
        while True:
            try:
                delay = float(input("Delay between readings in seconds? (default: 2): ") or "2")
                if delay >= 0:
                    break
                else:
                    print("Please enter a non-negative number")
            except ValueError:
                print("Please enter a valid number")
        
        print(f"\n🚀 Starting data collection...")
        print(f"   • {num_readings} reading(s) per sensor")
        print(f"   • {delay} second delay between readings")
        print(f"   • Data type: Calibrated spectral values")
        print(f"   • Total readings: {len(self.sensor_order) * num_readings}")
        
        # Prepare CSV file
        fieldnames = ['timestamp', 'sensor_id', 'sensor_position', 'reading_num', 'temperature'] + self.channel_names
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                total_readings = 0
                failed_readings = 0
                
                for sensor_pos, sensor_id in enumerate(self.sensor_order, 1):
                    print(f"\n📡 Scanning {sensor_id} (Position {sensor_pos}/{len(self.sensor_order)})")
                    
                    for reading_num in range(1, num_readings + 1):
                        print(f"   Reading {reading_num}/{num_readings}...", end=" ")
                        
                        # Get spectral data from sensor
                        data = self.get_sensor_data(sensor_id)
                        
                        if data and 'error' not in data:
                            # Prepare row for CSV
                            row = {
                                'timestamp': datetime.now().isoformat(),
                                'sensor_id': sensor_id,
                                'sensor_position': sensor_pos,
                                'reading_num': reading_num,
                                'temperature': data.get('temperature', 'N/A')
                            }
                            
                            # Add channel data
                            for i, channel_name in enumerate(self.channel_names):
                                row[channel_name] = data.get(f'CH{i}', 0)
                            
                            writer.writerow(row)
                            total_readings += 1
                            print("✅")
                        else:
                            failed_readings += 1
                            print("❌ Failed")
                            if data and 'error' in data:
                                print(f"      Error: {data['error']}")
                        
                        # Delay between readings (except after last reading of last sensor)
                        if not (sensor_pos == len(self.sensor_order) and reading_num == num_readings):
                            time.sleep(delay)
                
                print(f"\n🎉 Data collection complete!")
                print(f"   • Total successful readings: {total_readings}")
                print(f"   • Failed readings: {failed_readings}")
                print(f"   • Success rate: {(total_readings/(total_readings+failed_readings)*100):.1f}%")
                print(f"   • Data saved to: {os.path.abspath(filename)}")
                
                return True
                
        except Exception as e:
            print(f"\n❌ Error saving data: {e}")
            return False
    
    def get_sensor_data(self, sensor_id: str) -> Dict:
        """Get calibrated spectral data from a specific sensor"""
        try:
            # Send read command (simplified to only get calibrated data)
            responses = self.send_command_to_sensor(sensor_id, "READ_DATA", 3.0)
            
            if not responses:
                return {'error': 'No response from sensor'}
            
            # Parse response
            data = {}
            reading_data = False
            
            for line in responses:
                line = line.strip()
                
                if line == "DATA_START":
                    reading_data = True
                    continue
                elif line == "DATA_END":
                    reading_data = False
                    break
                elif reading_data and ":" in line:
                    try:
                        key, value = line.split(":", 1)
                        if key.startswith("CH"):
                            data[key] = float(value)
                        elif key == "TEMP":
                            data['temperature'] = int(value)
                        elif key == "SENSOR_ID":
                            data['sensor_id'] = value
                    except ValueError:
                        continue
                elif "ERROR" in line:
                    return {'error': line}
            
            if not data:
                return {'error': 'No valid data received'}
            
            return data
            
        except Exception as e:
            return {'error': f'Communication error: {e}'}
    
    def run_full_process(self):
        """Run the complete three-phase process"""
        print("🌈 AS7265x Spectral Sensor Data Collection System")
        print("=" * 70)
        print("Multi-sensor spectral data collection with automatic identification")
        print("and user-defined ordering for consistent data labeling.")
        print("📊 Collects CALIBRATED data only (factory calibrated spectral values)")
        
        try:
            # Find and connect to sensors
            print("\n🔍 STEP 1: Finding AS7265x sensors...")
            found_sensors = self.find_arduino_sensors()
            
            if not found_sensors:
                print("\n❌ No AS7265x sensors found!")
                print("Please check:")
                print("  • Arduino Nano 33 BLE boards are connected via USB")
                print("  • AS7265x sensors are properly connected to I2C pins")
                print("  • Sensors have adequate power supply")
                return False
            
            if not self.connect_to_sensors(found_sensors):
                return False
            
            # Phase 1: Identify sensors
            print("\n🔍 STEP 2: Sensor identification phase...")
            if not self.phase1_identify_sensors():
                return False
            
            # Phase 2: Get sensor order
            print("\n🔍 STEP 3: Define sensor order...")
            if not self.phase2_get_sensor_order():
                return False
            
            # Phase 3: Scan and save data
            print("\n🔍 STEP 4: Data collection...")
            if not self.phase3_scan_and_save():
                return False
            
            return True
            
        except KeyboardInterrupt:
            print("\n\n🛑 Process interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            return False
        finally:
            self.disconnect_all()

def main():
    """Main function to run the AS7265x data collection system"""
    print("🌈 AS7265x Spectral Sensor Data Collection System")
    print("=" * 70)
    print("This system will:")
    print("  1. 🔍 Find all connected AS7265x sensors")
    print("  2. 💡 Flash each sensor for identification")
    print("  3. 📝 Let you define the sensor order")
    print("  4. 📊 Collect CALIBRATED spectral data and save to CSV")
    print("\n📊 Note: This version only collects calibrated data (factory calibrated)")
    print("    spectral values, which is recommended for most applications.")
    print("\nMake sure all your Arduino Nano 33 BLE boards with AS7265x")
    print("sensors are connected and the Arduino code is uploaded.")
    
    input("\nPress Enter to start the process...")
    
    # Create controller and run
    controller = AS7265xController()
    success = controller.run_full_process()
    
    if success:
        print("\n🎉 Data collection completed successfully!")
        print("\nYour CSV file contains:")
        print("  • Timestamp for each reading")
        print("  • Sensor ID and position")
        print("  • Temperature readings")
        print("  • All 18 calibrated spectral channels (410nm - 940nm)")
        print("  • UV, Visible, and Near-Infrared data")
        print("  • Factory-calibrated values in µW/cm²")
    else:
        print("\n❌ Data collection failed!")
        print("Please check the error messages above and try again.")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()