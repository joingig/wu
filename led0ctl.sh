#!/bin/bash
led=/sys/class/leds/ACT/brightness
mmc0=/sys/class/leds/mmc0/brightness
if [ ! -n "$1" ]; then
    printf "Usage: $0 on|off \n"
    exit 100
fi

case "$1" in
on )
echo 1 | tee $mmc0 
echo 1 | tee $led 
printf "LED On\n"
;;
off )
echo 0 | tee $mmc0
echo 0 | tee $led 
printf "LED Off\n"
;;
* ) 
printf "Usage: $0 on|off \n" 
;;
esac
