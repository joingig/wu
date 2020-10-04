#!/bin/bash

#export wuhome=/root/wu
export wuhome=/home/tazz/wu
key=$wuhome/openweather.key

if [ ! -e $key ]; then
	printf "Openweathermap.org key not found in %s \n" $key 
        logger "$0 openweathermap.org key not found in $key"
	exit 100
fi
wkey=`head $key`
printf "key : %s\n" $wkey
/usr/bin/curl "api.openweathermap.org/data/2.5/weather?q=Moscow,ru&units=metric&appid=$wkey" -o $wuhome/openweather.json

python -c 'import sys, json, os; wuhome = os.environ.get("wuhome","/root/wu"); data_f = open(wuhome+"/openweather.json","r"); js_obj = json.load(data_f); print js_obj;'

if [ $? -eq 0 ]; then
    printf "No errors\n"
    exit 0;
fi

#we has some errors try after 5 min
printf "Sleep 5 min\n"
sleep 5m

/usr/bin/curl "api.openweathermap.org/data/2.5/weather?q=Moscow,ru&appid=$wkey" -o $wuhome/openweather.json
exit 0

