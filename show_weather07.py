"""Usage:
  show_weather04.py
  show_weather04.py night
  show_weather04.py -h | --help | --version
  show_weather04.py noip [--debug]
  show_weather04.py realtemp [--debug]
  show_weather04.py --debug

Options:
    noip                   skip ip cfg show
    night                  night mode, print time and exit
    realtemp               switch between temp_c feelslike_c
  -h --help                show this help message and exit
  --version                show version and exit
  --debug                  show debug info
"""

#maximum spaghetti code below

#_debug_ = False
#wuhome = "/home/tazz/wu" if _debug_ else "/root/wu"

setti = {'debug':False,
            'realtemp':False,
            'fname':"wu.pck",
            'wuhome':"/home/tazz/wu",
            'data_json':"openweather.json",
            'data_array':"dataa.txt"
           }

import sys
import csv
import json
import pickle
import socket
import psutil
import logging
import subprocess
#from urllib2 import urlopen, URLError
import  urllib.request
#from urllib import urlretrieve
from time import localtime, sleep, strftime
from os import getcwd, chdir, path
from docopt import docopt
from PIL import ImageFont, Image, ImageDraw, ImageFilter, ImageFile, ImageOps
from pymongo import * 

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

arguments = docopt(__doc__, version='0.016 EPD with Weatherstack API')

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

    #font_ttf30 = ImageFont.truetype(setti['wuhome']+"/luma/examples/fonts/C&C Red Alert [INET].ttf", 31)
    #font_ttf40 = ImageFont.truetype(setti['wuhome']+"/luma/examples/fonts/Volter__28Goldfish_29.ttf", 35)

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

    #print "font30.size {}".format(font30.getsize('255.255.255.255'))
    #sys.exit(0)

#fnk for image noise fight
def isLookstheSame (a, b, dev=10):
    if abs(a[0]-b[0]) < dev and abs(a[1]-b[1]) < dev and abs(a[2]-b[2]) < dev:
        return True
    return False

print("[*] Startup ok")
time = localtime()
hours = "0"+str(time.tm_hour) if time.tm_hour < 10 else str(time.tm_hour)
minutes = "0"+str(time.tm_min) if time.tm_min < 10 else str(time.tm_min)

#night mode between 01 and 06 am / we not showing weather / only time
if arguments['night']:
    time_and_exit("Deep night. Exiting.")

print("[*] Online") if internet_on() else time_and_exit("[*] We are offline. Exiting.")

#little buggy here docopt haz buildin -h help handler
#if arguments['--help']:
#    time_and_exit("[*] We are offline. Exiting.")


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
    sleep(2)

if getcwd() != setti['wuhome']:
    chdir(setti['wuhome'])
    if _debug_: print(getcwd())

#load settings
try:
    setti = pickle.load(open(setti['fname'], "rb"))
    if _debug_: print(setti)
except IOError as e:
    logger.error("I/O error({0}) {2}: {1}".format(e.errno, e.strerror, setti['fname']))
    logger.error("[*] creating {0}".format(setti['fname']))
    setti['cpws'] = None
    pickle.dump(setti, open(setti['fname'], "wb"))

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
last_upd = strftime("%a, %d %b %Y %H:%M:%S",localtime(parsed_json['dt'])) 
feelslike_c = round(parsed_json['main']["feels_like"], 1)
temp_c = round(parsed_json['main']["temp"], 1)
if len(parsed_json['weather'][0]['description']) == 0:
    logger.error("[*] look like weather_description is 0, mb json damaged.exiting")
    time_and_exit("[*] json error")

wdes = parsed_json['weather'][0]['description']
img_url = parsed_json['weather'][0]['icon']
#is_day = parsed_json['current']["is_day"]
#uv_index = parsed_json['current']['uv_index']
cloudcover = parsed_json['clouds']['all']
humidity = parsed_json['main']['humidity']
pressure = parsed_json['main']['pressure']
wind_speed = parsed_json['wind']['speed']
wind_dir = parsed_json['wind']['deg']
datetime = strftime("%a, %d %b %Y %H:%M:%S +0000",localtime(parsed_json['dt']))
weather_code = parsed_json['weather'][0]['id']

is_day = True if "d" in img_url else False

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
                    #print type(row)
                    #print row

                if line_count == 0:
                    print(f'Column names are {row}')
                    #print f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.'
                    #print '\t{} works in the {} department, and was born in {}.'.format(row["name"],row["department"],row["birthday month"])
                line_count += 1
            print(f'Processed {line_count} lines.')
    except (ValueError, IOError)as e:
        logger.error("Error read  CSV file {}, {}. Creating new".format(setti['data_array'],e))
#NEED KEYBOARD INPUT HERE like a YES/NO etc
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
if _debug_: logger.warning("Img url is {}".format(img_url))
if _debug_: logger.warning("Is day?: {}".format(is_day))

size_multipler = 1
img_url = "http://openweathermap.org/img/wn/{}@{}x.png".format(img_url,size_multipler) if size_multipler != 1 else "http://openweathermap.org/img/wn/{}.png".format(img_url)
img_a = img_url.split("/")[-1]

ImageFile.LOAD_TRUNCATED_IMAGES = True

if not path.isfile(img_a):
    print(f'Download {img_a}')
    urllib.request.urlretrieve(img_url, img_a)
   
    #pic = Image.open(setti['wuhome']+"/"+img_a)
    #pic_rgb = pic.convert("RGB")
    #r = pic_rgb.convert('L', dither=Image.NONE)
    #r.save('foo.bmp')

    #call ImageMagic for proper image converter
    #subprocess.check_call(['/usr/bin/convert', setti['wuhome']+"/"+img_a, '-colors 2 +dither', '-type bilevel', '-negate', setti['wuhome']+"/"+path.splitext(img_a)[0]+".bmp"])
    subprocess.check_call(['/usr/bin/convert', setti['wuhome']+"/"+img_a, '-colors', '2', '-type', 'bilevel', '-negate', setti['wuhome']+"/"+path.splitext(img_a)[0]+".bmp"])

if not _debug_:
    #with canvas(device) as draw:
    lastUp_txt = "|Upd: XXXXXXX" # + last_upd

    draw.text((200-font10.getsize(lastUp_txt)[0], 200-font10_s[1]-8),lastUp_txt, font = font10, fill = 255)
    #epd.display(epd.getbuffer(image.rotate(90)))
    sleep(2)

logger.warning("Current temperature in %s is: %s`C  %s, feels like: %s`C." % ( location, temp_c, wdes, feelslike_c))
logger.warning("Weather updated at {}".format(last_upd))

#dump config data
pickle.dump(setti, open(setti['fname'], "wb"))

temp_c = feelslike_c if not setti['realtemp'] else temp_c

#pic_a = Image.open(setti['wuhome']+"/"+img_a.split(".")[0]+".bmp")
pic_a = Image.open(setti['wuhome']+"/"+path.splitext(img_a)[0]+".bmp")

if not _debug_:
    image.paste(pic_a, (0, 85))
    draw.text((75, 85), str(temp_c)+u'`C', font = font30, fill = 0)
    draw.text((75, 120), hours+":"+minutes, font = font30, fill = 0)
    epd.display(epd.getbuffer(image.rotate(90)))

