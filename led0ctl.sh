#!/bin/bash

if [ ! -n "$1" ]; then
    printf "Usage: $0 on|off \n"
    exit 100
fi

case "$1" in
on )
echo mmc0 | tee /sys/class/leds/led0/trigger
echo 0 | tee /sys/class/leds/led0/brightness
printf "LED On\n"
;;
off )
echo none | tee /sys/class/leds/led0/trigger
echo 1 | tee /sys/class/leds/led0/brightness
printf "LED Off\n"
;;
* ) 
printf "Usage: $0 on|off \n" 
;;
esac
