#!/bin/bash

wuhome=/root/wu
#wuhome=/home/tazz/wu
key=$wuhome/apixu.key
days=2

if [ ! -e $key ]; then
	printf "apixu key not found in %s \n" $key 
        logger "$0 worldweatheronline key not found in $key"
	exit 100
fi
wkey=`head $key`
printf "key : %s\n" $wkey
/usr/bin/curl "http://api.apixu.com/v1/forecast.json?key=$wkey&q=Moscow&days=$days" -o $wuhome/apixu.json

python -c 'import sys, json, os; wuhome = os.environ.get("wuhome","/root/wu"); data_f = open(wuhome+"/apixu.json","r"); js_obj = json.load(data_f); print js_obj;'

if [ $? -eq 0 ]; then
    printf "No errors\n"
    exit 0;
fi

#we has some errors try after 5 min
printf "Sleep 5 min\n"
sleep 5m

/usr/bin/curl "http://api.apixu.com/v1/forecast.json?key=$wkey&q=Moscow&days=$days" -o $wuhome/apixu.json

exit 0

