#!/usr/bin/env python

import time
import smbus
import sys

bus = smbus.SMBus(1)
time.sleep(1)

SHT3x_ADDR		= 0x44
SHT3x_SS		= 0x2c
SHT3x_HIGH		= 0x06
SHT3x_READ		= 0x00

# MS to SL
bus.write_i2c_block_data(SHT3x_ADDR,SHT3x_SS,[0x06])
time.sleep(0.2)

# Read out data
data = bus.read_i2c_block_data(SHT3x_ADDR,SHT3x_READ,6)

# Devide data into counts Temperature
t_data = data[0] << 8 | data[1]

# Devide data into counts Humidity
h_data = data[3] << 8 | data[4]

# Convert counts to Temperature/Humidity
Hum = 100.0*float(h_data)/65535.0
Tem = -45.0 + 175.0*float(t_data)/65535.0

# Print Temperature and Humdity
#print("Temp: %0.2f C  H: %0.2f % ") % (Temperature,Humidity)
print(f"Temp: {Tem} C  H: {Hum}") 
