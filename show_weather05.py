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
            'cpws':"ISVIBLOV2",
            'hourly_h':0,
            'fname':"wu.pck",
            'pwsfile':"pws_list.txt",
            'wuhome':"/home/tazz/wu",
            'data_json':"weatherstack.json",
            'data_array':"dataa.txt"
           }

import sys
import csv
import json
import pickle
import socket
import psutil
import logging
from urllib2 import urlopen, URLError
from urllib import urlretrieve
from time import localtime, sleep
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
    print arguments
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
            urlopen('https://ya.ru', timeout=50)
            return True
        except URLError as err:
            pass
            if _debug_: print "internet check fail, {} try".format(m)
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

print "[*] Startup ok"
time = localtime()
hours = "0"+str(time.tm_hour) if time.tm_hour < 10 else str(time.tm_hour)
minutes = "0"+str(time.tm_min) if time.tm_min < 10 else str(time.tm_min)

#night mode between 01 and 06 am / we not showing weather / only time
if arguments['night']:
    time_and_exit("Deep night. Exiting.")

print "[*] Online" if internet_on() else time_and_exit("[*] We are offline. Exiting.")

#little buggy here docopt haz buildin -h help handler
#if arguments['--help']:
#    time_and_exit("[*] We are offline. Exiting.")


#db prepare
try:
    client = MongoClient('mongodb://localhost:27017/',connectTimeoutMS = 3000, socketTimeoutMS = 3000)
    db_si=client.server_info()
    if _debug_:
        logger.warning("Database info %s " % (db_si))
    db = client['dbweather']

#client.disconnect()
    if client.alive():
        print "db status {}".format(client.admin.command('ping'))
        print "db is alive" 
except:
    is_db = False
    print "[**] Database connection error."

#get if ip routine
if_l = psutil.net_if_addrs().keys()
if_a = psutil.net_if_addrs()
if _debug_: logger.warning("Avalable network interfaces %s" % (if_l))

if arguments['noip']:
    print "noip given"

if not _debug_:

    for key in if_l:
        #print "key %s" % (key)
        if "wlan" in key.lower():
            print "[**] found wlan %s %s" % (key, if_a[key][0].address)
            #if _debug_:  logger.warning("[**] found wlan %s %s" % (key, if_a[key][0].msgaddress))
            draw.text((0, 200-font10_s[1]-8), if_a[key][0].address, font = font10, fill="gray")
        if "eth" in key.lower() or "venet" in key.lower():
            print "[**] found ether %s %s" % (key, if_a[key][0].address)
            #if _debug_:  logger.warning("[**] found ether %s %s" % (key, if_a[key][0].msgaddress))
            draw.text((0, 200-font10_s[1]-8), if_a[key][0].address, font = font10,fill="gray")
    #epd.display(epd.getbuffer(image.rotate(90)))
    sleep(2)

if getcwd() != setti['wuhome']:
    chdir(setti['wuhome'])
    if _debug_: print getcwd()

#load settings
try:
    setti = pickle.load(open(setti['fname'], "rb"))
    if _debug_: print setti
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

if len(parsed_json['current']['weather_descriptions']) == 0:
    logger.error("[*] look like weather_descriptions is 0, mb json damaged.exiting")
    time_and_exit("[*] json error")

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
weather_code = parsed_json['current']['weather_code']

#collect data and write
fnames = ['datetime','uv_index','cloudcover','humidity','pressure','temperature','wind_speed','wind_dir']

if _debug_:
#debug
    try:
        with open(setti['data_array'], mode='ra') as f_da:
            csv_data = csv.DictReader(f_da,fieldnames=fnames)
            line_count = 0
            for row in csv_data:
                if _debug_:
                    print "line_count: {}".format(line_count)
                    #print type(row)
                    #print row

                if line_count == 0:
                    print 'Column names are {}'.format(row)
                    #print f'\t{row["name"]} works in the {row["department"]} department, and was born in {row["birthday month"]}.'
                    #print '\t{} works in the {} department, and was born in {}.'.format(row["name"],row["department"],row["birthday month"])
                line_count += 1
            print 'Processed {} lines.'.format(line_count)
    except (ValueError, IOError)as e:
        logger.error("Error read  CSV file {}, {}. Creating new".format(setti['data_array'],e))
#NEED KEYBOARD INPUT HERE like a YES/NO etc
        with open(setti['data_array'], mode='w') as f_da:
            csv_new = csv.writer(f_da, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csv_new.writerow(fnames)
            csv_new.writerow([datetime,uv_index,cloudcover,humidity,pressure,temp_c,wind_speed,wind_dir])
#write
try:
    with open(setti['data_array'], mode='a') as f_da:
        csv_new = csv.writer(f_da, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_new.writerow([datetime,uv_index,cloudcover,humidity,pressure,temp_c,wind_speed,wind_dir])
except (ValueError, IOError)as e:
    logger.error("Error write CSV file {}, {}.".format(setti['data_array'],e))
#end data collector 

#db write
try:
    t_data = db['data']
    print "t_data count() is {}".format(t_data.count())
    post_data = {
        'datetime':datetime,
        'uv_index':uv_index,
        'cloudcover':cloudcover,
        'humidity':humidity,
        'pressure':pressure,
        'temp_c':temp_c,
        'wind_speed':wind_speed,
        'wind_dir':wind_dir
    }

    result = t_data.insert(post_data)
    print('db post: {0}'.format(result))
except:
    print "[**] Database write error"
#end db write

#icon processing
if _debug_: logger.warning("Img url is {}".format(img_url))
if _debug_: logger.warning("Is day?: {}".format(is_day))

img_a = img_url.split("/")[-1]

ImageFile.LOAD_TRUNCATED_IMAGES = True
#attention, webp image with png extention 
#wsymbol_0008_clear_sky_night.png
#00000000: 01010010 01001001 01000110 01000110 10110000 00000000  RIFF..
#00000006: 00000000 00000000 01010111 01000101 01000010 01010000  ..WEBP
#0000000c: 01010110 01010000 00111000 00100000 10100100 00000000  VP8 .
#pillow need WEBP support from system libs
#
#from PIL import features
#print (features.check_module('webp'))
#True

if not path.isfile(img_a):
    print "Download %s" % (img_a)
    urlretrieve(img_url, img_a)
    if weather_code == 113:
        print "[**] Using weather113.png with weather code {} ".format(weather_code)
        #img_a = 'weather113.png'
    #start converting image 2 frenly format
    #pic = Image.open(img_a).resize((50,50))
    pic = Image.open(setti['wuhome']+"/"+img_a)
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
    newDataBW = []
    for item in data:
        #fight with noise background begin
        if isLookstheSame(pix, item, 14):
            #print "Looks the same {} and {}".format(pix,item)
            newData.append((255, 255, 255, 0))
            newDataBW.append((0,0,0))
        else:
            #print "Looks like {} and {} diff".format(pix,item)
            newData.append(item)
            newDataBW.append((255,255,255))

    pic_a.putdata(newData)
    pic_a.save(setti['wuhome']+"/wu"+img_a, "PNG")

    pic_b = pic_a.convert('1')
    pic_b.save(setti['wuhome']+"/bwB"+img_a.split(".")[0]+".bmp", "BMP")
  
    pic_c = Image.new("RGB", pic_a.size)
    pic_c.putdata(newDataBW)
    pic_c.convert('1').save(setti['wuhome']+"/c_"+img_a.split(".")[0]+".bmp", "BMP")

    #prepare EPD img
    pic_bw = pic.convert('1')
    pic_bw.save(setti['wuhome']+"/bw"+img_a.split(".")[0]+".bmp", "BMP")

    #end of converting routine

if not _debug_:
    #with canvas(device) as draw:
    lastUp_txt = " |Upd:" + last_upd.replace('Last Updated on ', '')

    draw.text((200-font10.getsize(lastUp_txt)[0], 200-font10_s[1]-8),lastUp_txt, font = font10, fill = 255)
    #epd.display(epd.getbuffer(image.rotate(90)))
    sleep(2)

logger.warning("Current temperature in %s is: %s`C  %s, feels like: %s`C." % ( location, temp_c, wdes, feelslike_c))
logger.warning("Weather updated at {}".format(last_upd))

#dump config data
pickle.dump(setti, open(setti['fname'], "wb"))

#if u'Mist' in wdes or u'Fog' in wdes:
#    #http://192.168.10.104:8800/c_wsymbol_0006_mist.bmp
#    img_a = 'c_wsymbol_0006_mist.bmp'
#    print "[**] using FOG/MIST reserved image {} because wdes == {}".format(img_a,wdes)

temp_c = feelslike_c if not setti['realtemp'] else temp_c

#if u'Yes' in is_day or u'yes' in is_day:
#    pic_a = Image.open(setti['wuhome']+"/bw"+img_a.split(".")[0]+".bmp")
#else:
pic_a = Image.open(setti['wuhome']+"/c_"+img_a.split(".")[0]+".bmp")

if not _debug_:
    #with canvas(device) as draw:
    #draw.bitmap((0, 0), pic_a, fill=5)
    #draw.text((60, 0), hours+":"+minutes, font=font_ttf30, fill="gray")
    #draw.text((60, 40), str(temp_c)+"`C", font=font_ttf30, fill="white")
    image.paste(pic_a, (0, 85))
    draw.text((75, 85), str(temp_c)+u'`C', font = font30, fill = 0)
    draw.text((75, 120), hours+":"+minutes, font = font30, fill = 0)
    epd.display(epd.getbuffer(image.rotate(90)))

#http://jsonviewer.stack.hu
