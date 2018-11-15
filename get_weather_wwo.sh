#!/bin/bash

wuhome=/root/wu
#wuhome=/home/tazz/wu

if [ ! -e $wuhome/wwo.key ]; then
	printf "worldweatheronline key not found in %s \n" $wuhome/wwo.key 
        logger "$0 worldweatheronline key not found in $wuhome/wwo.key"
	exit 100
fi
wkey=`head $wuhome/wwo.key`
printf "key : %s\n" $wkey
/usr/bin/curl "http://api.worldweatheronline.com/premium/v1/weather.ashx?key=$wkey&q=Moscow&format=json&num_of_days=3&&showlocaltime=yes" -o $wuhome/wwo00.json

