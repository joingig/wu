"""Usage:
  show_weather01.py
  show_weather01.py night
  show_weather01.py hourly [--next | --prev]
  show_weather01.py -h | --help | --version

Options:
  -h --help                show this help message and exit
  --version                show version and exit
  --next                   show next hour from "36 hours" weather report
  --prev                   show prev hour from "36 hours" weather report
"""

#
#maximum spaghetti code below

_debug_ = False
if _debug_:
    wuhome = "/home/tazz/wu"
else:
    wuhome = "/root/wu"
settings = {'cpws':"ISVIBLOV2",
            'hourly_h':0,
            'fname':"wu.pck",
            'pwsfile':"pws_list.txt"
           }

wwo = "wwo00.json"

import json
import sys
import pickle
import syslog as log
from urllib2 import urlopen, URLError
from urllib import urlretrieve
from time import localtime, sleep
from os import getcwd, chdir, path
from docopt import docopt

if not _debug_:
    from luma.core.serial import i2c
    from luma.core.render import canvas
    from luma.oled.device import ssd1306
    from PIL import ImageFont, Image

def internet_on():
    for m in range(1, 4):
        try:
            responsei = urlopen('https://ya.ru', timeout=5)
            return True
        except URLError as err: 
            pass
            print "internet check fail, {} try".format(m)
            log.syslog("Internet connection check failed")
        continue
    return False

def time_and_exit(mess):
    if not _debug_:
        with canvas(device) as draw:
            draw.text((20, 15), hours+":"+minutes, font=font_ttf40, fill="gray")
    sys.exit(mess)

if not _debug_:
    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial)
    font = ImageFont.load_default()
    font_ttf30 = ImageFont.truetype(wuhome+"/luma/examples/fonts/C&C Red Alert [INET].ttf", 30)
    font_ttf40 = ImageFont.truetype(wuhome+"/luma/examples/fonts/Volter__28Goldfish_29.ttf", 35)
    #device.contrast(220)

arguments = docopt(__doc__, version='0.5')
print(arguments)
print "[*] Startup ok"

time = localtime()

if time.tm_hour < 10:
    hours = "0"+str(time.tm_hour)
else:
    hours = str(time.tm_hour)

if time.tm_min < 10:
    minutes = "0"+str(time.tm_min)
else:
    minutes = str(time.tm_min)

#night mode between 01 and 06 am / we not showing weather / only time
#if time.tm_hour > 0 and time.tm_hour < 6:
if arguments['night']:
    time_and_exit("Deep night. Exiting.")

if internet_on():
    print "[*] Online"
else:
    time_and_exit("We are offline. Exiting.")

pwd = getcwd()
if pwd != wuhome:
    chdir(wuhome)
    print getcwd()

#load settings
try:
    settings = pickle.load(open(settings['fname'], "rb"))
except IOError as e:
    print "[**] I/O error({0}) {2}: {1}".format(e.errno, e.strerror, settings['fname'])
    print "[*] creating {0}".format(settings['fname'])
    settings['cpws'] = pws[0]
    pickle.dump(settings, open(settings['fname'], "wb"))


try:
    with open(wwo) as weather_file:
        parsed_json = json.load(weather_file)
        weather_file.close()
except (ValueError, IOError)as e:
    time_and_exit("[**] Error load JSON object. Exiting.")

location = parsed_json['data']["time_zone"][0]['zone']
last_upd = parsed_json['data']["time_zone"][0]['localtime']
current_condition = parsed_json['data']['current_condition']
flc = current_condition[0]['FeelsLikeC']
wdes = current_condition[0]['weatherDesc'][0]['value']
print "In {} is {}, feels like {}'C, time is {}".format(location,wdes,flc, last_upd)
img = current_condition[0]['weatherIconUrl'][0]['value']

#cat wwo00.json | jq .data.current_condition | more
#cat wwo00.json | jq .data.request | more

img_a = img.split("/")
sky_img = img_a[-1]

if not path.isfile(sky_img):
    print "Download %s" % (sky_img)
    urlretrieve(img, sky_img)

sys.exit(0)

if not _debug_:
    with canvas(device) as draw:
        draw.text((00, 20), cpws, font=font_ttf30, fill="gray")
        draw.text((00,55),last_upd.replace('Last Updated on ',''),font=font,fill="gray")
    sleep(1)
print "%s:%s Current temperature in %s is: %s`C  %s, feels like: %s`C" % (hours, minutes, location, temp_c, sky, feelslike_c)
print "{0}".format(last_upd)
log.syslog(cpws+" "+last_upd)
#dump config data
pickle.dump(settings, open(settings['fname'], "wb"))

if not _debug_:
    pic = Image.open(sky_img).convert("RGBA")
    with canvas(device) as draw:
#       draw.rectangle(device.bounding_box, outline="white", fill="black")
        draw.bitmap((0, 0), pic, fill=5)
        draw.text((60, 0), hours+":"+minutes, font=font_ttf30, fill="gray")
        draw.text((30, 40), str(temp_c)+"`C", font=font_ttf30, fill="white")

#raw_input("Press Enter to continue...")
#device.cleanup()

#http://jsonviewer.stack.hu
