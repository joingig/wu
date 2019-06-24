## RPi weather station
### Getting forecast part
First of, i stop using  [Weather Underground](https://www.wunderground.com/weather/api/d/docs) API beacose IBM have a plane to close free API, and now all Python code based on [Apixu Weather API](https://www.apixu.com/api.aspx). Apixu API dont have any [PWS](https://www.wunderground.com/weatherstation/overview.asp) analog , and now all PWS code removed. 
All Weather Underground legacy code you can find in  in show_weather01.py file, and working tree file now show_weather03.py.

SSD1306 driven with [LUMA](https://github.com/rm-hull/luma.oled) library with little modification (don't clear display after app close)

### Setup

Put yours [Apixu API key](https://www.apixu.com/api-explorer.aspx) to **apixu.key** file.

Add periodic task for PWS data refresh in you crontab as:
```sh
0  *\30  *  *  *  root   /usr/bin/python /home/tazz/wu/get_weather_apixu.sh
```
> Replace /home/tazz/wu/ with yours **wu** directory location.

> ***\30** mean every 30 minutes.

Add periodic task for LCD refresh/update in you crontab as:
```sh
0  *\5  *  *  *  root   /usr/bin/python /home/tazz/wu/show_weather03.py
```

### install requirements.txt
```sh
pip install -r requirements.txt
```


![pic_first_run](https://github.com/joingig/wu/blob/test/imgs/pic03.jpg "first")

