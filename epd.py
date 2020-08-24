#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os

#picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
#libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'e-Paper/RaspberryPi&JetsonNano/python/pic')
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'e-Paper/RaspberryPi&JetsonNano/python/lib')

if os.path.exists(libdir):
    sys.path.append(libdir)

#/home/tazz/wu/e-Paper/RaspberryPi\&JetsonNano/python/
print "[**] os.path.realpath {}".format(os.path.realpath(__file__))
print "[**] os.path.dirname(os.path.realpath(__file__)) {}".format(os.path.dirname(os.path.realpath(__file__)))
print "[**] picdir:{}, libdir:{}".format(picdir,libdir)

import logging
from waveshare_epd import epd1in54
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd1in54 Demo")
    
    epd = epd1in54.EPD()
    logging.info("init and Clear")
    epd.init(epd.lut_full_update)
    epd.Clear(0xFF)
    
    # Drawing on the image
    logging.info("1.Drawing on the image...")
    # '1' mode
    #1 (1-bit pixels, black and white, stored with one pixel per byte)
    #L (8-bit pixels, black and white)
    #P (8-bit pixels, mapped to any other mode using a color palette)
    #RGB (3x8-bit pixels, true color)
    #RGBA (4x8-bit pixels, true color with transparency mask)
    #CMYK (4x8-bit pixels, color separation)
    #YCbCr (3x8-bit pixels, color video format)
    
    image = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 24)
    font34 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 38)

    draw.rectangle((0, 10, 200, 52), fill = 0)
    draw.text((8, 12), 'hello world', font = font34, fill = 255)
    #draw.text((8, 44), u'微雪电子', font = font, fill = 0)
    #draw.line((16, 60, 56, 60), fill = 0)
    #draw.line((56, 60, 56, 110), fill = 0)
    #draw.line((16, 110, 56, 110), fill = 0)
    #draw.line((16, 110, 16, 60), fill = 0)
    #draw.line((16, 60, 56, 110), fill = 0)
    #draw.line((56, 60, 16, 110), fill = 0)
    draw.arc((90, 60, 150, 120), 0, 360, fill = 0)
    draw.rectangle((16, 130, 56, 180), fill = 0)
    draw.chord((90, 130, 150, 190), 0, 360, fill = 0)
    epd.display(epd.getbuffer(image.rotate(90)))
    time.sleep(2)
   

    # read bmp file 
    logging.info("2.read bmp file...")
    epd.Clear(0xFF)
    #image = Image.open(os.path.join(picdir, '1in54.bmp'))
    bmp = Image.open('bwwsymbol_0008_clear_sky_night.bmp')
    #epd.display(epd.getbuffer(image))
    image1 = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    #bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
    draw1 = ImageDraw.Draw(image1)
    #draw1.rectangle((0, 0, 200, 64), fill = 0)
    image1.paste(bmp, (0,0))
    draw1.text((75, 12), u'-17°C', font = font34, fill = 0)
    epd.display(epd.getbuffer(image1.rotate(90)))
    time.sleep(2)
    sys.exit(0)




    # read bmp file on window
    logging.info("3.read bmp file on window...")
    epd.Clear(0xFF)
    image1 = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
    bmp = Image.open(os.path.join(picdir, '100x100.bmp'))
    image1.paste(bmp, (50,50))    
    epd.display(epd.getbuffer(image1))
    time.sleep(2)
    
    # # partial update
    logging.info("4.show time...")
    epd.init(epd.lut_partial_update)    
    epd.Clear(0xFF)
    
    time_image = Image.new('1', (epd.width, epd.height), 255)
    time_draw = ImageDraw.Draw(time_image)
    num = 0
    while (True):
        time_draw.rectangle((10, 10, 120, 50), fill = 255)
        time_draw.text((10, 10), time.strftime('%H:%M:%S'), font = font, fill = 0)
        newimage = time_image.crop([10, 10, 120, 50])
        time_image.paste(newimage, (10,10))  
        epd.display(epd.getbuffer(time_image))
        num = num + 1
        if(num == 10):
            break
    
    logging.info("Clear...")
    epd.init(epd.lut_full_update)
    epd.Clear(0xFF)
    
    logging.info("Goto Sleep...")
    epd.sleep()
        
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd1in54.epdconfig.module_exit()
    exit()
