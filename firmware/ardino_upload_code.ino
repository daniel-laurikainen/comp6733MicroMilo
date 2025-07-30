#include <Wire.h>
#include <SparkFun_AS7265X.h>

AS7265X sensor;
// close sensor port number = 
// middle sensor port number = 
// far sensor port number = 

// colour order - black, red, white (inside out for cloUSBhub)
// String sensorID = "CloseSensor"; // /dev/cu.usbmodem11301 
String sensorID = "MiddleSensor"; // /dev/cu.usbmodem112301
// String sensorID = "FarSensor"; // /dev/cu.usbmodem112201
bool sensorFound = false;

void setup() {
  // CRITICAL: Match Python script's expected baud rate
  Serial.begin(9600);  // Changed back to 9600 to match Python script
  Wire.begin();

  // Wait for serial connection (Nano 33 BLE specific)
  unsigned long startTime = millis();
  while (!Serial && (millis() - startTime < 5000)) {
    delay(100);
  }
  delay(1000);

  // Initialize sensor using SparkFun library (same as your working code)
  if (sensor.begin()) {
    sensorFound = true;
    
    // Configure sensor settings
    sensor.setMeasurementMode(AS7265X_MEASUREMENT_MODE_4CHAN);
    sensor.setIntegrationCycles(49); // ~150ms integration time
    sensor.setGain(AS7265X_GAIN_64X); // 64x gain
    
    // Disable bulbs initially
    sensor.disableBulb(AS7265x_LED_WHITE);
    sensor.disableBulb(AS7265x_LED_IR);
    sensor.disableBulb(AS7265x_LED_UV);
  }
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
  delay(10);
}

void processCommand(String command) {
  command.toUpperCase();
  
  if (command == "PING") {
    Serial.println("PONG");
  }
  else if (command == "CHECK_SENSOR") {
    if (sensorFound) {
      Serial.println("SENSOR_OK");
    } else {
      Serial.println("SENSOR_ERROR");
    }
  }
  else if (command.startsWith("SET_ID ")) {
    String newID = command.substring(7);
    newID.trim();
    if (newID.length() > 0) {
      sensorID = newID;
      Serial.print("ID_SET:");
      Serial.println(sensorID);
    } else {
      Serial.println("ID_ERROR:Empty_ID");
    }
  }
  else if (command == "GET_ID") {
    Serial.print("ID:");
    Serial.println(sensorID);
  }
  else if (command == "LED_ON") {
    if (sensorFound) {
      sensor.enableBulb(AS7265x_LED_WHITE);
      sensor.enableBulb(AS7265x_LED_IR);
      sensor.enableBulb(AS7265x_LED_UV);
      Serial.println("LED_ON_OK");
    } else {
      Serial.println("LED_ERROR:No_Sensor");
    }
  }
  else if (command == "LED_OFF") {
    if (sensorFound) {
      sensor.disableBulb(AS7265x_LED_WHITE);
      sensor.disableBulb(AS7265x_LED_IR);
      sensor.disableBulb(AS7265x_LED_UV);
      Serial.println("LED_OFF_OK");
    } else {
      Serial.println("LED_ERROR:No_Sensor");
    }
  }
  else if (command == "LED_FLASH") {
    if (sensorFound) {
      flashLEDsWithStatus();
      Serial.println("LED_FLASH_OK");
    } else {
      Serial.println("LED_ERROR:No_Sensor");
    }
  }
  else if (command == "READ_DATA") {
  if (sensorFound) {
    readSpectralDataCompact();  // Sends CSV line for Python
  } else {
    Serial.println("SENSOR_ERROR");
  }
}

}

void flashLEDsWithStatus() {
  // Flash sequence with status messages that Python script expects
  Serial.print("FLASH_START:");
  Serial.println(sensorID);
  
  for (int i = 0; i < 3; i++) {
    sensor.enableBulb(AS7265x_LED_WHITE);
    sensor.enableBulb(AS7265x_LED_IR);
    sensor.enableBulb(AS7265x_LED_UV);
    
    Serial.print("FLASH_ON:");
    Serial.println(i + 1);
    delay(1000);
    
    sensor.disableBulb(AS7265x_LED_WHITE);
    sensor.disableBulb(AS7265x_LED_IR);
    sensor.disableBulb(AS7265x_LED_UV);
    
    Serial.print("FLASH_OFF:");
    Serial.println(i + 1);
    delay(500);
  }
  
  Serial.print("FLASH_END:");
  Serial.println(sensorID);
}

void readSpectralDataCompact() {
  sensor.takeMeasurements();

  float values[18] = {
    sensor.getCalibratedA(), sensor.getCalibratedB(),
    sensor.getCalibratedC(), sensor.getCalibratedD(),
    sensor.getCalibratedE(), sensor.getCalibratedF(),
    sensor.getCalibratedG(), sensor.getCalibratedH(),
    sensor.getCalibratedR(), sensor.getCalibratedI(),
    sensor.getCalibratedS(), sensor.getCalibratedJ(),
    sensor.getCalibratedT(), sensor.getCalibratedU(),
    sensor.getCalibratedV(), sensor.getCalibratedW(),
    sensor.getCalibratedK(), sensor.getCalibratedL()
  };

  for (int i = 0; i < 18; i++) {
    Serial.print(values[i], 4);  // 4 decimal precision
    if (i < 17) {
      Serial.print(",");
    }
  }
  Serial.println(); // newline after last value
}

