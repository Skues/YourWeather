import json
import os
import requests
from datetime import datetime, timedelta

BASE_URL = "http://api.openweathermap.org/data/2.5/"
FORECAST = "forecast?"
WEATHER = "weather?"
API_KEY = "b8f950e78f305c48801f6c82d5ed2a45"
TODAY_FILENAME = "weathertoday.json"
FORECAST_FILE = "weatherforecast.json"

class WeatherObject:
    def __init__(self):
        self.todaySet = False
        self.listSet = False
        self.today = {}
        self.list = []
        results = self._checkFiles(TODAY_FILENAME, FORECAST_FILE)
        if False in results:
            match results:
                case True, False:
                    self._updateToday(FORECAST, FORECAST_FILE)
                case False, True:
                    self._updateToday(WEATHER ,TODAY_FILENAME)
                case False, False:
                    self._updateToday(WEATHER, TODAY_FILENAME)
                    self._updateToday(FORECAST, FORECAST_FILE)
        self._setToday()
        self._setlist()

    def _setToday(self):
        if not self.todaySet:
            try:
                data = self.readWeather(filename="weathertoday.json")
                self.today = {"dt": data["dt"]}
                self.today.update(data["main"])
                self.today.update(data["wind"])
                self.todaySet = True
                self._checkDate(self.today["dt"])
            except Exception as err:
                print(err)

    def _checkFiles(self, *file):
        results = []
        for f in file:
            check = os.path.isfile(f)
            if not check:
                results.append(False)
            else:
                results.append(True)
        return results


    def _updateToday(self, addition, filename):
        url = BASE_URL + addition + "appid=" + API_KEY + "&q=SS6"
        r = requests.get(url).json()
        with open(filename, "w") as f:
            json.dump(r, f)

    def _checkDate(self, date):
        dateCheck = datetime.fromtimestamp(date)
        now = datetime.now()
        difference = now - dateCheck
        hour = timedelta(hours=1)
        if difference > hour:
            print("OUTDATED by an hour")
            self._updateToday(WEATHER, TODAY_FILENAME)
            self._setToday()
            self.todaySet = True
        else:
            return None


    def _setlist(self):
        if not self.listSet:
            try:
                data = self.readWeather(FORECAST_FILE)
                self.list = data["list"]
                self.listSet = True
            except Exception as err:
                print(err)

    def readWeather(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
            return data

    def kelvinToCelcius(self, kelvin):
        return round(kelvin-273.15, 2)

    def unixToUTC(self, unix):
        return datetime.fromtimestamp(unix)


    def __str__(self):
        return f"---------------\ndt: {self.unixToUTC(self.today["dt"])}\nTemp: {self.kelvinToCelcius(self.today["temp"])}\nFeels like: {self.kelvinToCelcius(self.today["feels_like"])}\n---------------"



url = BASE_URL + WEATHER + "appid=" + API_KEY + "&q=SS6"


def writeWeather(url):
    r = requests.get(url).json()
    with open("weather2.json", "w") as f:
        json.dump(r, f)



def indexOfTimes(listTimes, time):
    indexes = []
    for i in range(len(listTimes)):
        if listTimes[i].hour == time:
            indexes.append(i)
    return indexes



app = WeatherObject()
dateList = []
for item in app.list:
    dateList.append(app.unixToUTC(item["dt"]))
indexes = indexOfTimes(dateList, 22)
print(indexes)

# for i in range(2, len(app.list), 8):

#     print(i+1, app.unixToUTC(app.list[i]["dt"]).hour)
# print(app.unixToUTC(app.list[-1]["dt"])-app.unixToUTC(app.list[0]["dt"]))
