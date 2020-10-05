## RPi weather station
### application part on python
Forecast based on [Openweathermap](https://openweathermap.org/api) API

(1.54inch-e-paper)[https://www.waveshare.com/wiki/1.54inch_e-Paper_Module] driven with [DRV](https://github.com/waveshare/e-Paper)

### setup

Put yours [Openweathermap API key](https://home.openweathermap.org/api_keys) to **wu.key** file.

Add periodic task for weather data refresh in you crontab as:
```sh
0  *\30  *  *  *  root   /home/tazz/wu/get_weather.sh
```
> Replace /home/tazz/wu/ with yours **wu** directory location.

> ***\30** mean every 30 minutes.

Add periodic task for LCD refresh/update in you crontab as:
```sh
0  *\5  *  *  *  root   /usr/bin/python3 /home/tazz/wu/show_weather.py
```

![pic_first_run](https://github.com/joingig/wu/blob/test/imgs/pic03.jpg "first")

