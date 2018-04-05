#!/bin/bash

wuhome=/root/wu
#wuhome=/home/tazz/wu

pws=$wuhome/pws_list.txt
if [ ! -e $wuhome/wu.key ]; then
	printf "wunderground key not found in %s \n" $wuhome/wu.key 
        logger "$0 wunderground key not found in $wuhome/wu.key"
	exit 100
fi
wukkey=`head $wuhome/wu.key`
printf "key : %s\n" $wukkey
#for i in ${pws[@]}; do
for i in `cat $pws`; do
	printf $i
	if  echo $i | egrep -q -i "^#"
	then printf "\n%s commented out\n" $i; continue;
	fi
	/usr/bin/curl http://api.wunderground.com/api/$wukkey/geolookup/conditions/hourly/q/pws:$i.json -o $wuhome/$i.json
done

