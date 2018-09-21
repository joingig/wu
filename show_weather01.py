"""Usage:
  show_weather01.py
  show_weather01.py night
  show_weather01.py hourly [--next | --prev]
  show_weather01.py pwswitch
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

#settings_fname = "wu.pck"
# predefined PWS still needed?
pws = ["IMOSCOW36", "ISVIBLOV2", "IMOSKVA414", "IMOSKVA870", "I2310", "I1722", "IMOSCOW260"]

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
        except URLError as err: pass
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
#print(arguments)
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

#load pws_list
try:
    with open(settings['pwsfile']) as pws_list:
        data = pws_list.read()
        del pws[:]
        pws_new = []
        pws = data.split()
        pws_list.close()
        for pp in pws:
            if pp[0] != "#":
                print "{0} PWS OK".format(pp)
                pws_new.append(pp)
            else:
                print "{0} PWS removed".format(pp)
        if not pws_new:
            print "[**] Error load PWS list. Check {0} file.".format(settings['pwsfile'])
            #need workaround here for empty PWS list
        pws = pws_new
except (ValueError, IOError)as e:
    time_and_exit("[**] Error load " + settings['pwsfile'] + " Exiting.")

#load settings
try:
    settings = pickle.load(open(settings['fname'], "rb"))
except IOError as e:
    print "[**] I/O error({0}) {2}: {1}".format(e.errno, e.strerror, settings['fname'])
    print "[*] creating {0}".format(settings['fname'])
    settings['cpws'] = pws[0]
    pickle.dump(settings, open(settings['fname'], "wb"))

cpws = settings['cpws']

if cpws not in pws:
   print "PWS {} was removed, we fall back to begin list".format(cpws)
   cpws = pws[0]

if arguments['pwswitch']:
    print "[*] pws switch mode"
    le = len(pws)
    idx = pws.index(cpws)
    print "[*] pws len is {0}, cpws is {1}, index in pws is {2}".format(le, cpws, idx)
    if idx < le-1:
        idx += 1
    else:
        idx = 0
    cpws = settings['cpws'] = pws[idx] #save new pws
    # cpws = pws[idx] # renew cur pws with new value
    print "[*] idx is {0} and new cpws is {1}".format(idx, cpws)

print "[*] PWS: {0}".format(cpws)

#if not _debug_:
#    with canvas(device) as draw:
#        draw.text((00, 20), cpws, font=font_ttf30, fill="gray")
#        draw.text((00,55),"Last update",font=font,fill="gray")
#    sleep(1)

try:
    with open(cpws+".json") as pws_file:
        parsed_json = json.load(pws_file)
        pws_file.close()
except (ValueError, IOError)as e:
    time_and_exit("[**] Error load JSON object. Exiting.")

location = parsed_json['location']['city']
last_upd = parsed_json['current_observation']['observation_time']

if arguments['hourly']:
    print "[*] hourly mode"
    NextH = settings['hourly_h']
    print "[*] NextH is %s" % (NextH)
    try:
        temp_c = parsed_json['hourly_forecast'][NextH]['temp']['metric']
        feelslike_c = parsed_json['hourly_forecast'][NextH]['feelslike']['metric']
        sky = parsed_json['hourly_forecast'][NextH]['condition']
        img = parsed_json['hourly_forecast'][NextH]['icon_url']
        hours = parsed_json['hourly_forecast'][NextH]['FCTTIME']['hour']
        minutes = parsed_json['hourly_forecast'][NextH]['FCTTIME']['min']

        if arguments['--prev'] and NextH > 1:
            NextH -= 2
        else:
            NextH += 2
            if NextH == 34:
               NextH = 0

        settings['hourly_h'] = NextH
    except (IndexError) as e:
        print "[**] Error in data or hourly data loss\n[**] Try another PWS."
        temp_c = parsed_json['current_observation']['temp_c']
        feelslike_c = parsed_json['current_observation']['feelslike_c']
        sky = parsed_json['current_observation']['weather']
        img = parsed_json['current_observation']['icon_url']
        settings['hourly_h'] = 0

else:
    temp_c = parsed_json['current_observation']['temp_c']
    feelslike_c = parsed_json['current_observation']['feelslike_c']
    sky = parsed_json['current_observation']['weather']
    img = parsed_json['current_observation']['icon_url']
    #img_a = img.split("/");
    settings['hourly_h'] = 0

#for k  in img_a:
#       print k

img_a = img.split("/")
sky_img = img_a[len(img_a)-1]

if "nt_.gif" in sky_img: #nt_.gif is broken image on weather underground
    log.syslog("Image is corrupted "+sky_img)
    sky_img = "noun_sun01.gif"
print "Image file {0}".format(sky_img) 

if not path.isfile(sky_img):
    print "Download %s" % (sky_img)
    urlretrieve(img, sky_img)

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
