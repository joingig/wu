#!/bin/bash

#wuhome=/root/wu
wuhome=/home/tazz/wu
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

