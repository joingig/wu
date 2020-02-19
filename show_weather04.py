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

settings = {'debug':False,
            'realtemp':False,
            'cpws':"ISVIBLOV2",
            'hourly_h':0,
            'fname':"wu.pck",
            'pwsfile':"pws_list.txt",
            'wuhome':"/home/tazz/wu",
            'data_json':"weatherstack.json",
            'data_array':"dataa.txt"
           }

import json
import sys
import csv
import pickle
import socket
import psutil
import logging
from urllib2 import urlopen, URLError
from urllib import urlretrieve
from time import localtime, sleep
from os import getcwd, chdir, path
from docopt import docopt
from PIL import ImageFont, Image, ImageFilter, ImageFile

logger = logging.getLogger(__file__)

c_handler = logging.StreamHandler()
c_handler.setLevel(logging.WARNING)
c_format = logging.Formatter('%(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
logger.addHandler(c_handler)

f_handler = logging.FileHandler(settings['wuhome']+'/wu.log')
f_handler.setLevel(logging.ERROR)
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)

#i_handler = logging.StreamHandler()
#i_handler.setLevel(logging.DEBUG)
#i_format = logging.Formatter('%(levelname)s - %(message)s')
#i_handler.setFormatter(i_format)
#logger.addHandler(i_handler)

arguments = docopt(__doc__, version='0.014 with Weatherstack API')

if arguments['--debug']:
    _debug_ = True
    logger.warning("Debug is on")
    settings['debug']="True"
    print arguments
else:
    _debug_ = False
#    logger.warning("Debug is off")

if not _debug_:
    from luma.core.serial import i2c
    from luma.core.render import canvas
    from luma.oled.device import ssd1306

if _debug_:
    logger.warning('this is warning')
    logger.error('this is error')

def internet_on():
    """
    Check Internet connection.
    """
    for m in range(1, 4):
        try:
            urlopen('https://ya.ru', timeout=50)
            return True
        except URLError as err:
            pass
            if _debug_: print "internet check fail, {} try".format(m)
            #log.syslog("Internet connection check failed")
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
    serial = i2c(port=1, address=0x3C)
    device = ssd1306(serial)
    font = ImageFont.load_default()
    font_ttf30 = ImageFont.truetype(wuhome+"/luma/examples/fonts/C&C Red Alert [INET].ttf", 31)
    font_ttf40 = ImageFont.truetype(wuhome+"/luma/examples/fonts/Volter__28Goldfish_29.ttf", 35)
    #device.contrast(220)

#fnk for image noise fight
def isLookstheSame (a, b, dev=10):
    if abs(a[0]-b[0]) < dev and abs(a[1]-b[1]) < dev and abs(a[2]-b[2]) < dev:
        return True
    return False

print "[*] Startup ok"

time = localtime()

hours = "0"+str(time.tm_hour) if time.tm_hour < 10 else str(time.tm_hour)
minutes = "0"+str(time.tm_min) if time.tm_min < 10 else str(time.tm_min)

#night mode between 01 and 06 am / we not showing weather / only time
if arguments['night']:
    time_and_exit("Deep night. Exiting.")

if internet_on():
    print "[*] Online"
else:
    time_and_exit("[*] We are offline. Exiting.")

#little buggy here docopt haz buildin -h help handler
#if arguments['--help']:
#    time_and_exit("[*] We are offline. Exiting.")

if_l = psutil.net_if_addrs().keys()
if_a = psutil.net_if_addrs()
#print "[**] Avalable network interfaces %s" % (if_l)
if _debug_: logger.warning("Avalable network interfaces %s" % (if_l))

if arguments['noip']:
    print "noip given"

if not _debug_:
    with canvas(device) as draw:
        draw.text((0, 0), '__ IP CFG __', font=font, fill="gray")
        for key in if_l:
            #print "key %s" % (key)
            if "wlan" in key.lower():
                print "[**] found wlan %s %s" % (key, if_a[key][0].address)
                #if _debug_:  logger.warning("[**] found wlan %s %s" % (key, if_a[key][0].msgaddress))
                draw.text((00, 20), if_a[key][0].address, font=font, fill="gray")
            if "eth" in key.lower() or "venet" in key.lower():
                print "[**] found ether %s %s" % (key, if_a[key][0].address)
                #if _debug_:  logger.warning("[**] found ether %s %s" % (key, if_a[key][0].msgaddress))
                draw.text((00,30), if_a[key][0].address, font=font,fill="gray")
    sleep(2)

if getcwd() != settings['wuhome']:
    chdir(settings['wuhome'])
    if _debug__: print getcwd()

#load settings
try:
    settings = pickle.load(open(settings['fname'], "rb"))
    if _debug_: print settings
except IOError as e:
    #print "[**] I/O error({0}) {2}: {1}".format(e.errno, e.strerror, settings['fname'])
    #print "[*] creating {0}".format(settings['fname'])
    logger.error("I/O error({0}) {2}: {1}".format(e.errno, e.strerror, settings['fname']))
    logger.error("[*] creating {0}".format(settings['fname']))
    settings['cpws'] = None
    pickle.dump(settings, open(settings['fname'], "wb"))

#load weather json file
try:
    with open(settings['data_json']) as weather_file:
        parsed_json = json.load(weather_file)
except (ValueError, IOError)as e:
    logger.error("Error load JSON object in {}.".format(settings['data_json']))
    time_and_exit("[**] Error load JSON object. Exiting.")

#swithch realtemp/feelslike trigger
if arguments['realtemp']:
    #if _debug_: print "[*] realtemp is {}, switching ".format(settings['realtsdfsdfsfemp'])
    if _debug_: logger.warning("[*] realtemp is {}, switching ".format(settings['realtemp']))
    settings['realtemp'] = not settings['realtemp']
#else:
#    print "[*] Default mode, using feelslike_c {} for temperature".format(feelslike_c)
#    temp_c = feelslike_c

#"datetime" "uv_index" "cloudcover" "humidity" "pressure" "temperature" "wind_speed" "wind_dir"
location = parsed_json['location']['timezone_id']
last_upd = parsed_json['current']['observation_time']
feelslike_c = parsed_json['current']["feelslike"]
temp_c = parsed_json['current']["temperature"]
wdes = parsed_json['current']['weather_descriptions'][0]
img_url = parsed_json['current']['weather_icons'][0]
is_day = parsed_json['current']["is_day"]
uv_index = parsed_json['current']['uv_index']
cloudcover = parsed_json['current']['cloudcover']
humidity = parsed_json['current']['humidity']
pressure = parsed_json['current']['pressure']
wind_speed = parsed_json['current']['wind_speed']
wind_dir = parsed_json['current']['wind_dir']
datetime = parsed_json['location']['localtime']

#collect data and write
fnames = ['datetime','uv_index','cloudcover','humidity','pressure','temperature','wind_speed','wind_dir']
try:
    with open(settings['data_array'], mode='ra') as f_da:
        csv_data = csv.DictWriter(f_da,fieldnames=fnames)
        line_count = 0
        for row in csv_data:
            if _debug_:
                print "line_count: {}".format(line_count)
                print type(row)
                print row

            if line_count == 0:
                print 'Column names are {}'.format(row)
            #print f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.'
            #print '\t{} works in the {} department, and was born in {}.'.format(row["name"],row["department"],row["birthday month"])
            line_count += 1
        print 'Processed {} lines.'.format(line_count)
        print 'Write data'


        csv_data = csv.DictWriter(f_da,fieldnames=fnames)
        csv_data.writerow([datetime,uv_index,cloudcover,humidity,pressure,temp_c,wind_speed,wind_dir])
except (ValueError, IOError)as e:
    logger.error("Error load CSV file {}, {}. Creating new".format(settings['data_array']),e)
    with open(settings['data_array'], mode='w') as f_da:
        csv_new = csv.writer(f_da, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_new.writerow(fnames)
        csv_new.writerow([datetime,uv_index,cloudcover,humidity,pressure,temp_c,wind_speed,wind_dir])

if _debug_: logger.warning("Img url is {}".format(img_url))
if _debug_: logger.warning("Is day?: {}".format(is_day))

img_a = img_url.split("/")[-1]

ImageFile.LOAD_TRUNCATED_IMAGES = True

if not path.isfile(img_a):
    print "Download %s" % (img_a)
    urlretrieve(img_url, img_a)

    #start converting image 2 frenly format
    #pic = Image.open(img_a).resize((50,50))
    pic = Image.open(img_a)
    pic_a = pic.convert("RGBA")
    data = pic_a.getdata()

    #pix is a background start/etalon pixel
    pix = data[5]
    print "[**] pix data: {}".format(pix)

    #(197, 197, 197, 255)
    #(147, 147, 147, 255)
    #(64, 72, 145, 255)
    #print pic_a.mode

    newData = []
    for item in data:
        #fight with noise background begin
        if isLookstheSame(pix, item, 13):
            #print "Looks the same {} and {}".format(pix,item)
            newData.append((255, 255, 255, 0))
        else:
            #print "Looks like {} and {} diff".format(pix,item)
            newData.append(item)

    #old background replace routine
    #if item[0] == 197 and item[1] == 197 and item[2] == 197:
    #if item[0] == pix[0] and item[1] == pix[1] and item[2] == pix[2]:
    #if item == pix or item == pix2 or item == pix3:
    #    newData.append((255, 255, 255, 0))
    #else:
    #    newData.append(item)
    pic_a.putdata(newData)
    pic_a.save("wu"+img_a, "PNG")
    #end of converting routine

if not _debug_:
    with canvas(device) as draw:
        draw.text((00, 55), last_upd.replace('Last Updated on ', ''), font=font, fill="gray")
    sleep(1)

#print "%s:%s Current temperature in %s is: %s`C  %s, feels like: %s`C." % (hours, minutes, location, temp_c, wdes, feelslike_c, )
logger.warning("Current temperature in %s is: %s`C  %s, feels like: %s`C." % ( location, temp_c, wdes, feelslike_c))
#print "[*] Weather updated at %s" % (last_upd)
#log.syslog("Weather updated at "+last_upd)
logger.warning("Weather updated at {}".format(last_upd))

#dump config data
pickle.dump(settings, open(settings['fname'], "wb"))

if u'Mist' in wdes or u'Fog' in wdes:
    img_a = 'wu_noun_fog00.png'
    print "[**] using FOG/MIST reserved image {} because wdes == {}".format(img_a,wdes)

#if arguments['realtemp']:
#    print "[*] realtemp is on, using temp_c {} for temperaure".format(temp_c)
#else:
#    print "[*] Default mode, using feelslike_c {} for temperature".format(feelslike_c)
#    temp_c = feelslike_c
temp_c = feelslike_c if not settings['realtemp'] else temp_c

pic_a = Image.open('wu'+img_a)

if not _debug_:
    with canvas(device) as draw:
        draw.bitmap((0, 0), pic_a, fill=5)
        draw.text((60, 0), hours+":"+minutes, font=font_ttf30, fill="gray")
        draw.text((60, 40), str(temp_c)+"`C", font=font_ttf30, fill="white")

#http://jsonviewer.stack.hu
