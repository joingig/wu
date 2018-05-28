## RPi weather station
### application part on python
Forecast based on [Weather Underground](https://www.wunderground.com/weather/api/d/docs) API (Personal Weather Station(aka PWS)+location+hourly)

SSD1306 driven with [LUMA](https://github.com/rm-hull/luma.oled) library with little modification (don't clear display after app close)

### setup

Put yours [Weather Underground key api](https://www.wunderground.com/weather/api/d/docs) to **wu.key** file.

Add periodic task for PWS data refresh in you crontab as:
```sh
0  *\30  *  *  *  root   /usr/bin/python /home/tazz/wu/get_weather.sh
```
> Replace /home/tazz/wu/ with yours **wu** directory location.

> ***\30** mean every 30 minutes.

Add periodic task for LCD refresh/update in you crontab as:
```sh
0  *\5  *  *  *  root   /usr/bin/python /home/tazz/wu/show_weather01.py
```

### install requirements.txt
```sh
pip install -r /path/to/requirements.txt
```


![pic_first_run](https://github.com/joingig/wu/blob/test/imgs/pic03.jpg "first")

