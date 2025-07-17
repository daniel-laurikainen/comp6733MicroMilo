from machine import Pin, I2C
import time

# I2C on Nano 33 BLE Sense Rev2 (default: A4 = SDA, A5 = SCL)
i2c = I2C(0, scl=Pin(27), sda=Pin(26))  # Confirm pin numbers for your firmware

AS7265X_ADDR = 0x49
AS7265X_HW_VERSION = 0x00
AS7265X_SLAVE_STATUS_REG = 0x00
AS7265X_SLAVE_WRITE_REG = 0x01
AS7265X_SLAVE_READ_REG = 0x02
AS7265X_TX_VALID = 0x02
AS7265X_RX_VALID = 0x01
AS7265X_WRITE = 0x01
AS7265X_READ = 0x02

def read_virtual_register(virtual_reg):
    # Wait for TX buffer to be ready
    while i2c.readfrom_mem(AS7265X_ADDR, AS7265X_SLAVE_STATUS_REG, 1)[0] & AS7265X_TX_VALID:
        pass
    i2c.writeto_mem(AS7265X_ADDR, AS7265X_SLAVE_WRITE_REG, bytes([virtual_reg | AS7265X_READ]))
    # Wait for RX buffer to have data
    while not i2c.readfrom_mem(AS7265X_ADDR, AS7265X_SLAVE_STATUS_REG, 1)[0] & AS7265X_RX_VALID:
        pass
    return i2c.readfrom_mem(AS7265X_ADDR, AS7265X_SLAVE_READ_REG, 1)[0]

def write_virtual_register(virtual_reg, value):
    while i2c.readfrom_mem(AS7265X_ADDR, AS7265X_SLAVE_STATUS_REG, 1)[0] & AS7265X_TX_VALID:
        pass
    i2c.writeto_mem(AS7265X_ADDR, AS7265X_SLAVE_WRITE_REG, bytes([virtual_reg | AS7265X_WRITE]))
    while i2c.readfrom_mem(AS7265X_ADDR, AS7265X_SLAVE_STATUS_REG, 1)[0] & AS7265X_TX_VALID:
        pass
    i2c.writeto_mem(AS7265X_ADDR, AS7265X_SLAVE_WRITE_REG, bytes([value]))

def start_measurement():
    # Enable all 3 AS7265x devices and auto gain, continuous mode
    write_virtual_register(0x04, 0b00110100)  # LED current limit
    write_virtual_register(0x07, 0x03)        # Enable all devices
    write_virtual_register(0x04, 0x3C)        # Continuous mode

def read_all_channels():
    # 18 channels: Read from registers 0x08 to 0x21
    channels = {}
    labels = [
        'R', 'S', 'T', 'U', 'V', 'W',  # AS72651
        'A', 'B', 'C', 'D', 'E', 'F',  # AS72652
        'G', 'H', 'I', 'J', 'K', 'L'   # AS72653
    ]
    for i in range(18):
        high = read_virtual_register(0x08 + i * 2)
        low = read_virtual_register(0x08 + i * 2 + 1)
        value = (high << 8) | low
        channels[labels[i]] = value
    return channels

# Main program
print("Starting AS7265x spectral scan...")
start_measurement()
time.sleep(1)

while True:
    data = read_all_channels()
    for ch, val in data.items():
        print(f"{ch}: {val}", end=" | ")
    print("\n")
    time.sleep(2)
