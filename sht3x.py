import time
#import smbus
import smbus2
import sys

#sht3x
SHT3x_ADDR              = 0x44
SHT3x_SS                = 0x2c
SHT3x_HIGH              = 0x06
SHT3x_READ              = 0x00

def sht3x_init(SHT3x_ADDR: int, SHT3x_SS: int) -> None:
    global bus 
    bus = smbus2.SMBus(1)
    time.sleep(2)
    # MS to SL
    bus.write_i2c_block_data(SHT3x_ADDR,SHT3x_SS,[0x06])
    time.sleep(2)
    pass


def sht3x_get(SHT3x_ADDR: int, SHT3x_READ: int):
    # Read out data
    data = bus.read_i2c_block_data(SHT3x_ADDR,SHT3x_READ,6)

    # Devide data into counts Temperature
    t_data = data[0] << 8 | data[1]

    # Devide data into counts Humidity
    h_data = data[3] << 8 | data[4]

    # Convert counts to Temperature/Humidity
    global Hum
    global Tem
    Hum = 100.0*float(h_data)/65535.0
    Tem = -45.0 + 175.0*float(t_data)/65535.0
    pass

# Print Temperature and Humdity
#print("Temp: %0.2f C  H: %0.2f % ") % (Temperature,Humidity)
sht3x_init(SHT3x_ADDR, SHT3x_SS)
sht3x_get(SHT3x_ADDR, SHT3x_READ)
print(f"Temperature: {Tem} C  Humidity: {Hum}")
