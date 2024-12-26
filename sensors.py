from subprocess import check_output
from sys import executable
from os import path
import threading
import time
import mh_z19
import smbus2

##HDC1000 Sensor routine (Temperature, Humidity)
##if _debug_:
#print(f'[**] Init HDC1000 Sensor')
#hdc1000 = SDL_Pi_HDC1000.SDL_Pi_HDC1000()
#hdc1000.turnHeaterOn()
#hdc1000.turnHeaterOff()
#hdc1000.setTemperatureResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_TEMPERATURE_RESOLUTION_11BIT)
#hdc1000.setTemperatureResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_TEMPERATURE_RESOLUTION_14BIT)
#hdc1000.setHumidityResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_HUMIDITY_RESOLUTION_8BIT)
#hdc1000.setHumidityResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_HUMIDITY_RESOLUTION_14BIT)
#hdc1000_data = {'t':0.0,'h':0.0}
#def t_hdc1000():
#    t_name = threading.currentThread().getName()
#    print(f'[**]Thread name {t_name}')
#    t_start = time.time()
#    t_finish = t_start + 10
#    tick = 0
#    while t_start + tick < t_finish:
#        #print( "-----------------")
#        #print( "Temperature = %3.1f C" % hdc1000.readTemperature())
#        #print( "Humidity = %3.1f %%" % hdc1000.readHumidity())
#        #print( "-----------------")
#        print(f'{time.strftime("%H:%M:%S")} Humidity: {hdc1000.readHumidity()}, Temperature: {hdc1000.readTemperature()}, iteration: {tick}')
#        time.sleep(1.0)
#        tick += 1
#        hdc1000_data['t'] +=  hdc1000.readTemperature()
#        hdc1000_data['h'] +=  hdc1000.readHumidity()
#    hdc1000_data['t'] /=  tick
#    hdc1000_data['h'] /=  tick
#    print(f"[**]Average t {hdc1000_data['t']}, h {hdc1000_data['h']}")
#    pass

##CCS811 Sensor routine (eCO2, TVOC, Temperature)
##if _debug_:
#print(f'[**] Init CCS811 Sensor')
#ccs811_data = {'co2':0.0, 'tvoc':0.0, 't':0.0}
#i2c = busio.I2C(board.SCL, board.SDA)
#print(f'[**]i2c {i2c}')
#ccs811 = adafruit_ccs811.CCS811(i2c)
#
## Wait for the sensor to be ready
#while not ccs811.data_ready:
#    pass
#
#def t_ccs811():
#    t_name = threading.currentThread().getName()
#    print(f'[**]Thread name {t_name}')
#    t_start = time.time()
#    t_finish = t_start + 10
#    tick = 0
#    while t_start + tick < t_finish:
#        #print("{} CO2: {} PPM, TVOC: {} PPB, Temp: {}, iteration {}".format(time.strftime('%H:%M:%S'), ccs811.eco2, ccs811.tvoc, ccs811.temperature, tick))
#        print(f'{time.strftime("%H:%M:%S")} CO2: {ccs811.eco2} PPM, TVOC: {ccs811.tvoc}, Temperature: {ccs811.temperature}, iteration: {tick}')
#        time.sleep(5.0)
#        ccs811_data['co2'] += ccs811.eco2
#        ccs811_data['tvoc'] += ccs811.tvoc
#        ccs811_data['t'] += ccs811.temperature
#        tick += 1
#
#    ccs811_data['co2'] /= tick
#    ccs811_data['tvoc'] /= tick
#    ccs811_data['t'] /= tick
#    print(f"[**]Average CO2 {ccs811_data['co2']}, TVOC {ccs811_data['tvoc']}, Temperature {ccs811_data['t']}")
#    pass

#MH_Z19 Sensor routine (CO2, PPM, Temperature)
#if _debug_:
mhz19_data = {'co2':0.0, 't':0.0}
def t_mhz19():
    global mhz19_g
    #mhz19_data = {'co2':0.0, 't':0.0}
    t_name = threading.currentThread().getName()
    print(f'[**]Thread name {t_name}')
    t_start = time.time()
    t_finish = t_start + 25
    tick = 0
    while t_start + tick < t_finish:
         mhz19 = mh_z19.read_all()
         print(f'{time.strftime("%H:%M:%S")} CO2: {mhz19["co2"]} PPM, Temperature: {mhz19["temperature"]}, iteration: {tick}')
         time.sleep(2.0)
         mhz19_data['co2'] += mhz19['co2']
         mhz19_data['t'] += mhz19['temperature']
         tick += 1

    mhz19_data['co2'] /= tick
    mhz19_data['t'] /= tick
    mhz19_g = mhz19_data.copy()
    print(f"[**]Average co2 {mhz19_g['co2']}, temperature {mhz19_g['t']}")
    pass

#SHT3x workarround
def sht3x() -> []:
    sht3x_py = path.join(path.dirname(path.realpath(__file__)), 'sht3x.py')
    cmd = ' '.join([executable, sht3x_py])
    out = check_output(cmd.split())
    out_sp = out.decode().split()
    print('[**]', out.decode().split())
    return out_sp 

#SHT3s sensor routine, humidity and temp
SHT3x_ADDR              = 0x44
SHT3x_SS                = 0x2c
SHT3x_HIGH              = 0x06
SHT3x_READ              = 0x00
def t_sht3x():
    #bus = smbus.SMBus(1)
    #time.sleep(1)

    #SHT3x_ADDR              = 0x44
    #SHT3x_SS                = 0x2c
    #SHT3x_HIGH              = 0x06
    #SHT3x_READ              = 0x00
    global sht3x_g
    sht3x_data = {'h':0.0, 't':0.0}

    with smbus2.SMBus(1) as bus:
        # MS to SL
        bus.write_i2c_block_data(SHT3x_ADDR,SHT3x_SS,[0x06])
        time.sleep(0.2)

        t_start = time.time()
        t_finish = t_start + 25
        tick = 0
        while t_start + tick < t_finish:
            data = bus.read_i2c_block_data(SHT3x_ADDR,SHT3x_READ,6)
            t_data = data[0] << 8 | data[1]
            h_data = data[3] << 8 | data[4]
            sht3x_data['h'] += 100.0*float(h_data)/65535.0
            sht3x_data['t'] += -45.0 + 175.0*float(t_data)/65535.0
            time.sleep(1.0)
            tick += 1

    sht3x_data['h'] /= tick
    sht3x_data['t'] /= tick
    sht3x_g = sht3x_data.copy()
    print(f"[**]Average humidity:{sht3x_g['h']}, temperature:{sht3x_['t']}")
    pass
