#!/bin/bash

dir=/root/wu
pws=$dir/pws_list.txt
wukkey=`head wu.key`

printf "key : %s\n" $wukkey
#for i in ${pws[@]}; do
for i in `cat $pws`; do
	printf $i
	/usr/bin/curl http://api.wunderground.com/api/$wukkey/geolookup/conditions/hourly/q/pws:$i.json -o $dir/$i.json
done


#ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3 | head -1` > /dev/null && echo ok || echo error
#ping -q -w 1 -c 1 8.8.8.8 > /dev/null && echo ok || echo error

#function ping_gw() { ping -q -w 1 -c 1 `ip r | grep default | cut -d ' ' -f 3 | head -1` > /dev/null && return 0 || return 1} 

#ping_gw || (echo "no network, bye" && exit 1)