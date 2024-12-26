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

from sys import path as syspath
import csv
import json
import time
import pickle
#import socket
from psutil import net_if_addrs
import logging
import subprocess
import urllib.request
from os import getcwd, chdir, path, listdir
from docopt import docopt
from PIL import ImageFont, Image, ImageDraw, ImageFilter, ImageFile, ImageOps
import threading
#import SDL_Pi_HDC1000
#import board
#import busio
#import adafruit_ccs811
#import mh_z19
#import smbus2
from sensors import t_mhz19, sht3x, t_sht3x, mhz19_data

picdir = path.join(path.dirname(path.realpath(__file__)),'e-Paper/RaspberryPi&JetsonNano/python/pic')
libdir = path.join(path.dirname(path.realpath(__file__)),'e-Paper/RaspberryPi&JetsonNano/python/lib')

if path.exists(libdir):
    syspath.append(libdir)

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

home_icon = ''.join([setti['wuhome'],'/imgs/',setti['home_icon']])
print(f'Home icon: {home_icon}')
if path.isfile(home_icon):
    if path.splitext(setti['home_icon'])[1]=='.png':
        print(f'[**] Convert:{home_icon} to 50x50 BMP')
        call_magic(home_icon, False, False, True, "50x50")
        home_icon_bmp = ''.join([setti['wuhome'],'/imgs/',path.splitext(setti['home_icon'])[0],'.bmp'])

#TODO image manipulation FIX needed
line_w = 4 
pic_h = Image.new('1', (60, 60), 255)  # 255: clear the frame
#Domik
pic_h_draw = ImageDraw.Draw(pic_h)
pic_h_draw.rounded_rectangle([(5,15), (55,55)], radius=4, width=line_w)
pic_h_draw.rounded_rectangle([(20,25), (40,45)], radius=4, width=line_w)
pic_h_draw.line([(1,15), (30,1)], width=line_w)
pic_h_draw.line([(30,1), (60,15)], width=line_w)

#MHZ19 sensor routine, co2 and temperature
#if _debug_:
mhz19_g = {'co2':0.0, 't':0.0}
print(f'[*] Init MH_Z19 Sensor')
mhz19_thread  = threading.Thread(target=t_mhz19, name='t_mhz19')
mhz19_thread.start()

#SHT3s sensor routine, humidity and temperature 
#sht3x_g = {'h':0.0, 't':0.0}
print(f'[*] Init SHT3x Sensor')
sht3x_g = sht3x()
#broken smbus funk multithreading
#sht3x_thread  = threading.Thread(target=t_sht3x, name='t_sht3x')
#sht3x_thread.start()

cur_time = time.localtime()
hours = f'0{cur_time.tm_hour}' if cur_time.tm_hour < 10 else str(cur_time.tm_hour)
minutes = f'0{cur_time.tm_min}' if cur_time.tm_min < 10 else str(cur_time.tm_min)

print(f'[*] Online') if internet_on() else time_and_exit("[*] We are offline. Exiting.")
print(f'[*] Startup ok')

#get ip 
if_l = net_if_addrs().keys()
if_a = net_if_addrs()
if _debug_: logger.warning(f"Avalable network interfaces {if_l}")

if arguments['noip']:
    print("noip given")

#swithch realtemp/feelslike trigger
if arguments['realtemp']:
    logger.warning("realtemp is {}, switching ".format(setti['realtemp']))
    setti['realtemp'] = not setti['realtemp']

if not _debug_:
    for key in if_l:
        #print "key %s" % (key)
        if "wlan" in key.lower():
            print(f'[*] {key} {if_a[key][0].address}')
            #if _debug_:  logger.warning("[**] found wlan %s %s" % (key, if_a[key][0].msgaddress))
            draw.text((0, 200-font10_s[1]-8), if_a[key][0].address, font = font10, fill="gray")
        if "eth" in key.lower() or "venet" in key.lower():
            print(f'[*] Ether {key} {if_a[key][0].address}') 
            #if _debug_:  logger.warning("[**] found ether %s %s" % (key, if_a[key][0].msgaddress))
            draw.text((0, 200-font10_s[1]-8), if_a[key][0].address, font = font10,fill="gray")
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
    logger.error(f"Error load JSON object in {settings['data_json']}")
    time_and_exit("[**] Error load JSON object. Exiting.")

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
cloud_cover = parsed_json['clouds']['all']
humidity = parsed_json['main']['humidity']
pressure = parsed_json['main']['pressure']
wind_speed = parsed_json['wind']['speed']
wind_dir = parsed_json['wind']['deg']
date_time = time.strftime('%a %d %b %Y %H:%M:%S',time.localtime())
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
            csv_new.writerow([date_time,cloud_cover,humidity,pressure,temp_c,wind_speed,wind_dir])
#write
try:
    with open(setti['data_array'], mode='a') as f_da:
        csv_new = csv.writer(f_da, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_new.writerow([date_time,cloud_cover,humidity,pressure,temp_c,wind_speed,wind_dir])
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

while mhz19_thread.is_alive():
    pass
print('[**]MH_Z19 thread finish.')

if not _debug_:
    image.paste(pic_a, (0, 85))

    draw.text((1, 1), f"co2 {mhz19_data['co2']}", font = font20, fill = 255)
    draw.text((70, 30), f"t: {mhz19_data['t']:.2f}`C", font = font20, fill = 0)
    draw.text((70, 53), f'h: {sht3x_g[4][0:5]}%', font = font20, fill = 0)
#    draw.text((70, 53), f"h: not ready%", font = font20, fill = 0)
    image.paste(pic_h, (5, 30)) 
    draw.text((75, 85), str(temp_c)+u'`C', font = font30, fill = 0)
    draw.text((80, 120), f'{hours}:{minutes}', font = font30, fill = 0)
    #image.paste(pic_a, (0, 70))
    epd.display(epd.getbuffer(image.rotate(90)))
