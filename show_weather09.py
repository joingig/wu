"""Usage:
  show_weather.py
  show_weather.py night
  show_weather.py -h | --help | --version
  show_weather.py noip [--debug]
  show_weather.py realtemp [--debug]
  show_weather.py --debug
  show_weather.py mkbmp

Options:
    noip                   skip ip cfg show
    night                  night mode, print time and exit
    realtemp               switch between temp_c feelslike_c
  -h --help                show this help message and exit
  --version                show version and exit
  --debug                  show debug info
    mkbmp                  recreate BMP's from PNG
"""
#need new cmd options review

#maximum spaghetti code below

setti = {'debug':False,
            'realtemp':False,
            'fname':"wu.pck",
            'wuhome':"/home/tazz/wu",
            'data_json':"openweather.json",
            'data_array':"dataa.txt",
            'home_icon':"noun_Home_1564976.png"
           }

import sys
import csv
import json
import time
import pickle
import socket
import psutil
import logging
import subprocess
import urllib.request
from os import getcwd, chdir, path, listdir
from docopt import docopt
from PIL import ImageFont, Image, ImageDraw, ImageFilter, ImageFile, ImageOps
#from pymongo import * 
import threading
#sensors import
import SDL_Pi_HDC1000
import board
import busio
import adafruit_ccs811
import mh_z19

picdir = path.join(path.dirname(path.realpath(__file__)),'e-Paper/RaspberryPi&JetsonNano/python/pic')
libdir = path.join(path.dirname(path.realpath(__file__)),'e-Paper/RaspberryPi&JetsonNano/python/lib')

if path.exists(libdir):
        sys.path.append(libdir)

from waveshare_epd import epd1in54

logger = logging.getLogger(__file__)

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.WARNING)
c_format = logging.Formatter('%(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)

f_handler = logging.FileHandler("{}{}".format(setti['wuhome'],"/wu.log"))
f_handler.setLevel(logging.ERROR)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)

arguments = docopt(__doc__, version='0.9 EPD with Weatherstack API and HDC1000 CCS811 sensors')

if arguments['--debug']:
    _debug_ = True
    logger.warning("Debug is on")
    setti['debug']="True"
    print(arguments)
else:
    _debug_ = False

if _debug_:
    logger.warning('this is warning')
    logger.error('this is error')

def internet_on():
    """
    Check Internet connection.
    """
    for m in range(1, 4):
        try:
            urllib.request.urlopen('https://ya.ru', timeout=50)
            return True
        except urllib.request.HTTPerror as err:
            pass
            if _debug_: print(f'internet check fail, {m} try')
            logger.error("Internet connection check failed")
        continue
    return False

def time_and_exit(mess):
    """
    Print current time and exit
    """
    if not _debug_:
        with canvas(device) as draw:
            draw.text((20, 15), hours+":"+minutes, font=font_ttf40, fill="gray")
    sys.exit(mess)

if not _debug_:
    epd = epd1in54.EPD()
    epd.init(epd.lut_full_update)
    #epd.Clear(0xFF)

    image = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    
    font10 = ImageFont.truetype(path.join(picdir, 'Font.ttc'), 14)
    font20 = ImageFont.truetype(path.join(picdir, 'Font.ttc'), 24)
    font30 = ImageFont.truetype(path.join(picdir, 'Font.ttc'), 38)
   
    font10_s = font10.getsize('255.255.255.255')
    font20_s = font20.getsize('255.255.255.255')
    font30_s = font30.getsize('255.255.255.255')

    draw.rectangle((0, 0, 200, font20_s[1]+4), fill = 0)
    draw.rectangle((0, 200-font20_s[1]-4, 200,200), fill = 0)


#call ImageMagic for PNG to BMP convert
#https://legacy.imagemagick.org/Usage/quantize/#monochrome
def call_magic(pic_name, negate=True, crop=True, resize=False, r_size='80x80'):
    #cmd = ' '.join(['/usr/bin/convert', pic_name, '-colors', '2', '-type', 'bilevel'])
    cmd = ' '.join(['/usr/bin/convert', pic_name])

    if resize:
        cmd += ' '.join([' -adaptive-resize', r_size])
    
    if crop:
        cmd += ' -gravity Center -crop 80x80%'

    #cmd += ' '.join([' -colors', '2', '-colorspace', 'gray', '-normalize'])
    #cmd += ' '.join([' -colorspace', 'gray', '+dither', '-colors 2', '-type bilevel', '-normalize'])
    cmd += ' '.join([' -colorspace', 'gray', '+dither', '-colors 2', '-type bilevel', '-normalize'])
    #cmd += ' '.join([' -colors', '2', '-type', 'bilevel'])

    if negate:
        cmd += ' -negate'
     
    cmd += ' '+path.splitext(pic_name)[0]+'.bmp'
    
    print(f'[**] call_magic with {cmd.split()}') 
    subprocess.check_call(cmd.split())
    pass

#load settings
try:
    setti = pickle.load(open(setti['wuhome']+'/'+setti['fname'], "rb"))
    if _debug_: print(f'[**]Settings: {setti}')
except IOError as e:
    logger.error("I/O error({0}) {2}: {1}".format(e.errno, e.strerror, setti['fname']))
    logger.error("[*] creating {0}".format(setti['fname']))
    pickle.dump(setti, open(setti['wuhome']+'/'+setti['fname'], "wb"))

if arguments['mkbmp']:
    print('[*] mkbmp given')
    #TODO
    #make png's list
    for f in listdir(setti['wuhome']):
        if f.endswith('.png'):
            print(f)
            call_magic(f, True, True, True)

    for fi in listdir(setti['wuhome']+'/imgs'):
        if fi.endswith('.png'):
            print(fi)
            call_magic('imgs/'+fi, False, False, True)
    print('[*]Done. Exiting.')
    sys.exit(0)


#########################################################################################


#home_icon = setti['wuhome'] + '/imgs/' + setti['home_icon']
home_icon = ''.join([setti['wuhome'],'/imgs/',setti['home_icon']])
print(f'Home icon: {home_icon}')
if path.isfile(home_icon):
    if path.splitext(setti['home_icon'])[1]=='.png':
        print(f'[**] Convert:{home_icon} to 50x50 BMP')
        call_magic(home_icon, False, False, True, "50x50")
        home_icon_bmp = ''.join([setti['wuhome'],'/imgs/',path.splitext(setti['home_icon'])[0],'.bmp'])
        #pic_h = Image.open(home_icon_bmp)
#TODO image manipulation FIX needed
line_w = 4 
pic_h = Image.new('1', (60, 60), 255)  # 255: clear the frame
pic_h_draw = ImageDraw.Draw(pic_h)
pic_h_draw.rounded_rectangle([(5,15), (55,55)], radius=4, width=line_w)
pic_h_draw.rounded_rectangle([(20,25), (40,45)], radius=4, width=line_w)
pic_h_draw.line([(1,15), (30,1)], width=line_w)
pic_h_draw.line([(30,1), (60,15)], width=line_w)


#HDC1000 Sensor routine
#if _debug_:
print(f'[**] Init HDC1000 Sensor')
hdc1000 = SDL_Pi_HDC1000.SDL_Pi_HDC1000()
hdc1000.turnHeaterOn()
hdc1000.turnHeaterOff()
hdc1000.setTemperatureResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_TEMPERATURE_RESOLUTION_11BIT)
hdc1000.setTemperatureResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_TEMPERATURE_RESOLUTION_14BIT)
hdc1000.setHumidityResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_HUMIDITY_RESOLUTION_8BIT)
hdc1000.setHumidityResolution(SDL_Pi_HDC1000.HDC1000_CONFIG_HUMIDITY_RESOLUTION_14BIT)
hdc1000_data = {'t':0.0,'h':0.0}
def t_hdc1000():
    t_name = threading.currentThread().getName()
    print('f[**]Thread name {t_name}')
    t_start = time.time()
    t_finish = t_start + 10
    tick = 0
    while t_start + tick < t_finish:
        #print( "-----------------")
        #print( "Temperature = %3.1f C" % hdc1000.readTemperature())
        #print( "Humidity = %3.1f %%" % hdc1000.readHumidity())
        #print( "-----------------")
        print(f'{time.strftime("%H:%M:%S")} Humidity: {hdc1000.readHumidity()}, Temperature: {hdc1000.readTemperature()}, iteration: {tick}')
        time.sleep(1.0)
        tick += 1
        hdc1000_data['t'] +=  hdc1000.readTemperature()
        hdc1000_data['h'] +=  hdc1000.readHumidity()
    hdc1000_data['t'] /=  tick
    hdc1000_data['h'] /=  tick
    print(f"[**]Average t {hdc1000_data['t']}, h {hdc1000_data['h']}")
    pass

hdc1000_thread  = threading.Thread(target=t_hdc1000, name='t_hdc1000')
hdc1000_thread.start()

#CCS811 Sensor routine
#if _debug_:
print(f'[**] Init CCS811 Sensor')
ccs811_data = {'co2':0.0, 'tvoc':0.0, 't':0.0}
i2c = busio.I2C(board.SCL, board.SDA)
print(f'[**]i2c {i2c}')
ccs811 = adafruit_ccs811.CCS811(i2c)

# Wait for the sensor to be ready
while not ccs811.data_ready:
    pass

def t_ccs811():
    t_name = threading.currentThread().getName()
    print('f[**]Thread name {t_name}')
    t_start = time.time()
    t_finish = t_start + 10 
    tick = 0
    while t_start + tick < t_finish:
        #print("{} CO2: {} PPM, TVOC: {} PPB, Temp: {}, iteration {}".format(time.strftime('%H:%M:%S'), ccs811.eco2, ccs811.tvoc, ccs811.temperature, tick))
        print(f'{time.strftime("%H:%M:%S")} CO2: {ccs811.eco2} PPM, TVOC: {ccs811.tvoc}, Temperature: {ccs811.temperature}, iteration: {tick}')
        time.sleep(5.0)
        ccs811_data['co2'] += ccs811.eco2
        ccs811_data['tvoc'] += ccs811.tvoc
        ccs811_data['t'] += ccs811.temperature
        tick += 1 
   
    ccs811_data['co2'] /= tick 
    ccs811_data['tvoc'] /= tick 
    ccs811_data['t'] /= tick 
    print(f"[**]Average CO2 {ccs811_data['co2']}, TVOC {ccs811_data['tvoc']}, Temperature {ccs811_data['t']}")
    pass
ccs811_thread  = threading.Thread(target=t_ccs811, name='t_ccs811')
ccs811_thread.start()


#MH_Z19 Sensor routine
#if _debug_:
mhz19_data = {'co2':0.0, 't':0.0}
print(f'[**] Init MH_Z19 Sensor')
def t_mhz19():
    t_name = threading.currentThread().getName()
    print('f[**]Thread name {t_name}')
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
    print(f"[**]Average co2 {mhz19_data['co2']}, temperature {mhz19_data['t']}")
    pass
mhz19_thread  = threading.Thread(target=t_mhz19, name='t_mhz19')
mhz19_thread.start()

print("[*] Startup ok")
cur_time = time.localtime()
hours = "0"+str(cur_time.tm_hour) if cur_time.tm_hour < 10 else str(cur_time.tm_hour)
minutes = "0"+str(cur_time.tm_min) if cur_time.tm_min < 10 else str(cur_time.tm_min)

#night mode between 01 and 06 am / we not showing weather / only time
#if arguments['night']:
#    time_and_exit("Deep night. Exiting.")

print("[*] Online") if internet_on() else time_and_exit("[*] We are offline. Exiting.")

#get if ip routine
if_l = psutil.net_if_addrs().keys()
if_a = psutil.net_if_addrs()
if _debug_: logger.warning("Avalable network interfaces %s" % (if_l))

if arguments['noip']:
    print("noip given")

if not _debug_:
    for key in if_l:
        #print "key %s" % (key)
        if "wlan" in key.lower():
            print(f'[*] Wlan {key} {if_a[key][0].address}')
            #if _debug_:  logger.warning("[**] found wlan %s %s" % (key, if_a[key][0].msgaddress))
            draw.text((0, 200-font10_s[1]-8), if_a[key][0].address, font = font10, fill="gray")
        if "eth" in key.lower() or "venet" in key.lower():
            print(f'[*] Ether {key} {if_a[key][0].address}') 
            #if _debug_:  logger.warning("[**] found ether %s %s" % (key, if_a[key][0].msgaddress))
            draw.text((0, 200-font10_s[1]-8), if_a[key][0].address, font = font10,fill="gray")
    #epd.display(epd.getbuffer(image.rotate(90)))
    time.sleep(2)

#go home
if getcwd() != setti['wuhome']:
    chdir(setti['wuhome'])
    if _debug_: print(getcwd())

#MAIN
#load weather json file
try:
    with open(setti['data_json']) as weather_file:
        parsed_json = json.load(weather_file)
except (ValueError, IOError)as e:
    logger.error("Error load JSON object in {}.".format(settings['data_json']))
    time_and_exit("[**] Error load JSON object. Exiting.")

#swithch realtemp/feelslike trigger
if arguments['realtemp']:
    logger.warning("realtemp is {}, switching ".format(setti['realtemp']))
    setti['realtemp'] = not setti['realtemp']
#else:
#    print "[*] Default mode, using feelslike_c {} for temperature".format(feelslike_c)
#    temp_c = feelslike_c

#root@rpiz:/home/tazz/wu# jq ."sys"."country" < openweather.json  | more
#"RU"
#root@rpiz:/home/tazz/wu# jq ."name" < openweather.json  | more
#"Moscow"

#"datetime" "uv_index" "cloudcover" "humidity" "pressure" "temperature" "wind_speed" "wind_dir"
location = parsed_json['name']
last_upd = time.strftime("%a, %d %b %Y %H:%M:%S",time.localtime(parsed_json['dt'])) 
feelslike_c = round(parsed_json['main']["feels_like"], 1)
temp_c = round(parsed_json['main']["temp"], 1)
if len(parsed_json['weather'][0]['description']) == 0:
    logger.error("[*] look like weather_description is 0, mb json damaged.exiting")
    time_and_exit("[*] json error")

wdes = parsed_json['weather'][0]['description']
img_icon = parsed_json['weather'][0]['icon']
#is_day = parsed_json['current']["is_day"]
#uv_index = parsed_json['current']['uv_index']
cloudcover = parsed_json['clouds']['all']
humidity = parsed_json['main']['humidity']
pressure = parsed_json['main']['pressure']
wind_speed = parsed_json['wind']['speed']
wind_dir = parsed_json['wind']['deg']
datetime = time.strftime("%a, %d %b %Y %H:%M:%S +0000",time.localtime(parsed_json['dt']))
weather_code = parsed_json['weather'][0]['id']

is_day = True if "d" in img_icon else False

#collect data and write
fnames = ['datetime','cloudcover','humidity','pressure','temperature','wind_speed','wind_dir']

if _debug_:
#debug
    try:
        with open(setti['data_array'], mode='ra') as f_da:
            csv_data = csv.DictReader(f_da,fieldnames=fnames)
            line_count = 0
            for row in csv_data:
                if _debug_:
                    print(f'line_count: {line_count}')

                if line_count == 0:
                    print(f'Column names are {row}')
                    #print f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.'
                    #print '\t{} works in the {} department, and was born in {}.'.format(row["name"],row["department"],row["birthday month"])
                line_count += 1
            print(f'Processed {line_count} lines.')
    except (ValueError, IOError)as e:
        logger.error("Error read  CSV file {}, {}. Creating new".format(setti['data_array'],e))
#TODO NEED KEYBOARD INPUT HERE like a YES/NO etc
        with open(setti['data_array'], mode='w') as f_da:
            csv_new = csv.writer(f_da, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_new.writerow(fnames)
            csv_new.writerow([datetime,cloudcover,humidity,pressure,temp_c,wind_speed,wind_dir])
#write
try:
    with open(setti['data_array'], mode='a') as f_da:
        csv_new = csv.writer(f_da, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_new.writerow([datetime,cloudcover,humidity,pressure,temp_c,wind_speed,wind_dir])
except (ValueError, IOError)as e:
    logger.error("Error write CSV file {}, {}.".format(setti['data_array'],e))
#end data collector 

#icon processing
if _debug_: logger.warning("Img url: {}".format(img_icon))
if _debug_: logger.warning("Is day?: {}".format(is_day))

size_multipler = 2
img_url = "http://openweathermap.org/img/wn/{}@{}x.png".format(img_icon,size_multipler) if size_multipler != 1 else "http://openweathermap.org/img/wn/{}.png".format(img_icon)
img_a = img_url.split("/")[-1]

if not path.isfile(img_a):
    print(f'Download {img_a}')
    urllib.request.urlretrieve(img_url, img_a)
   
    #call ImageMagic for proper image converter
    #TODO 03n,03d images dont need invert (-negate key)
    #TODO 50d image bad convertion with IM 6.9.10-23 Q16 arm 20190101
    call_magic(img_a, True, True)

#if path.isfile(setti['wuhome'] + 'imgs/' + setti['home_icon']):
#    home_icon_bmp = setti['wuhome'] + '/imgs/' +path.splitext(setti['home_icon'])[0]+'.bmp'
#    print(f'[**] home icon:{home_icon_bmp}')
#    pic_h = Image.open(home_icon_bmp)

if not _debug_:
    lastUp_txt = "|Upd: XXXXXXX" # + last_upd
    draw.text((200-font10.getsize(lastUp_txt)[0], 200-font10_s[1]-8),lastUp_txt, font = font10, fill = 255)
    time.sleep(2)

logger.warning("Current temperature in %s is: %s`C  %s, feels like: %s`C." % ( location, temp_c, wdes, feelslike_c))
logger.warning("Weather updated at {}".format(last_upd))

#dump config data
pickle.dump(setti, open(setti['fname'], "wb"))

temp_c = feelslike_c if not setti['realtemp'] else temp_c

pic_a = Image.open(setti['wuhome']+"/"+path.splitext(img_a)[0]+".bmp")

while hdc1000_thread.is_alive():
    pass
print('[**]HDC1000 thread finish.')

while ccs811_thread.is_alive():
    pass
print('[**]CCS811 thread finish.')

while mhz19_thread.is_alive():
    pass
print('[**]MH_Z19 thread finish.')

if not _debug_:
    image.paste(pic_a, (0, 85))

    draw.text((1, 1), f"co2 {mhz19_data['co2']}", font = font20, fill = 255)

    draw.text((70, 30), f"t: {mhz19_data['t']:.2f}`C", font = font20, fill = 0)
    draw.text((70, 53), f"h: {hdc1000_data['h']:.2f}%", font = font20, fill = 0)
    image.paste(pic_h, (5, 30)) 
    draw.text((75, 85), str(temp_c)+u'`C', font = font30, fill = 0)
    draw.text((80, 120), hours+":"+minutes, font = font30, fill = 0)
    #image.paste(pic_a, (0, 70))
    epd.display(epd.getbuffer(image.rotate(90)))
