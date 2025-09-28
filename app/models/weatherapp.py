import json
import os
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

BASE_URL = "http://api.openweathermap.org/data/2.5/"
FORECAST = "forecast?"
WEATHER = "weather?"
API_KEY = os.environ.get("OPENWEATHER_API_KEY")
WEATHER_FILENAME = "weathertoday.json"
FORECAST_FILENAME = "weatherforecast.json"
WEATHER_LIST = ["dt", "main", "wind", "name"]
FORECAST_LIST = ["list", "city"]


class WeatherObject:
    def __init__(self, location="United Kingdom"):
        self.location = location
        self.todaySet = False
        self.listSet = False
        self.today = {}
        self.list = {}
        error = ""
        updateList = [[WEATHER, WEATHER_FILENAME], [FORECAST, FORECAST_FILENAME]]
        for update in updateList:
            error = self._updateFile(update[0], update[1])
            if error != "":
                logger.error(error)
                return error

        # results = self._checkFiles(WEATHER_FILENAME, FORECAST_FILENAMENAME)
        # if False in results:
        #     match results:
        #         case True, False:
        #             self._updateFile(FORECAST, FORECAST_FILENAMENAME)
        #         case False, True:
        #             self._updateFile(WEATHER ,WEATHER_FILENAME)
        #         case False, False:
        #             self._updateFile(WEATHER, WEATHER_FILENAME)
        #             self._updateFile(FORECAST, FORECAST_FILENAME)
        self._setter(WEATHER, FORECAST)

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
                logger.error(err)

    def _setlist(self):
        if not self.listSet:
            try:
                data = self.readWeather(FORECAST_FILENAME)
                self.list = data["list"]
                self.listSet = True
            except Exception as err:
                logger.error(err)

    def _setter(self, *addition):
        if len(addition) == 1:
            if addition[0] == WEATHER:
                if not self.todaySet:
                    data = self.readWeather(WEATHER_FILENAME)
                    for i in WEATHER_LIST:
                        self.today[i] = data[i]
                self.todaySet = True

            elif addition[0] == FORECAST:

                logger.info("Recevied forecast")
                if not self.listSet:
                    logger.info("List not set")
                    data = self.readWeather(FORECAST_FILENAME)
                    for i in FORECAST_LIST:
                        self.list[i] = data[i]
                    logger.info("Setting list")
                self.listSet = True

        elif len(addition) > 1:
            if not self.todaySet:
                data = self.readWeather(WEATHER_FILENAME)
                for i in WEATHER_LIST:
                    self.today[i] = data[i]
            if not self.listSet:
                data = self.readWeather(FORECAST_FILENAME)
                for i in FORECAST_LIST:
                    self.list[i] = data[i]
            self.todaySet = True
            self.listSet = True

    def _checkFiles(self, *file):
        results = []
        for f in file:
            check = os.path.isfile(f)
            if not check:
                results.append(False)
            else:
                results.append(True)
        return results

    def _updateFile(self, addition, filename):
        url = BASE_URL + addition + "appid=" + API_KEY + f"&q={self.location}"
        logger.info(f"Location: {self.location}")
        r = requests.get(url).json()
        if str(r["cod"]) != "200":
            logger.error(r["message"])
            return r["message"]
        else:
            with open(filename, "w") as f:
                json.dump(r, f)
            return ""

    def _checkDate(self, date):
        dateCheck = datetime.fromtimestamp(date)
        now = datetime.now()
        difference = now - dateCheck
        hour = timedelta(hours=1)
        if difference > hour:
            logger.info("Outdated, updating now")
            self._updateFile(WEATHER, WEATHER_FILENAME)
            self.todaySet = False
            self._setter(WEATHER)
            self.todaySet = True
        else:
            return None

    def readWeather(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
            return data

    def kelvinToCelcius(self, kelvin):
        if kelvin < 100:
            return kelvin
        return int(round(kelvin - 273.15, 0))

    def unixToUTC(self, unix):
        day = datetime.fromtimestamp(unix).weekday()
        match day:
            case 0:
                day = "Monday"
            case 1:
                day = "Tuesday"
            case 2:
                day = "Wednesday"
            case 3:
                day = "Thursday"
            case 4:
                day = "Friday"
            case 5:
                day = "Saturday"
            case 6:
                day = "Sunday"
        return f"{day} {datetime.fromtimestamp(unix).strftime("%d/%m, %H:%M")}"

    def indexOfTimes(self, listTimes, time):
        indexes = []
        for i in range(len(listTimes)):
            if f"{str(time)}:" in listTimes[i]["dt"]:
                indexes.append(i)
        return indexes
        for i in range(len(listTimes)):
            if listTimes[i].hour == time:
                indexes.append(i)
        return indexes

    def setLocation(self, addition, location):
        if addition == "forecast":

            addition = FORECAST
            filename = FORECAST_FILENAME
            self.listSet = False
        elif addition == "today":
            addition = WEATHER
            filename = WEATHER_FILENAME
            self.todaySet = False
        self.location = location
        error = self._updateFile(addition, filename)
        if error != "":
            logger.error(error)
            return error
        self._setter(addition)
        self.listTemperatureFix(self.list["list"])
        self.listTimeFix(self.list["list"])
        return ""

    def listTemperatureFix(self, list):
        if list[0]["main"]["temp"] < 100:
            return None
        temperatures = ["temp", "feels_like", "temp_min", "temp_max"]
        for i in range(len(list)):
            for t in temperatures:
                list[i]["main"][t] = self.kelvinToCelcius(list[i]["main"][t])

    def listTimeFix(self, list):
        if type(list[0]["dt"]) is str:
            return None
        for i in range(len(list)):
            list[i]["dt"] = self.unixToUTC(list[i]["dt"])

    def errorCheck(self, data):
        if data["cod"] != "200":
            return data["message"]
        else:
            return ""

    def min_maxTemperatures(self, list):
        list[0]["main"]["temp_max"]
        list[0]["main"]["temp_min"]
        grouped = {}
        for item in list:
            if item["dt_txt"].split()[0] in grouped:
                grouped[item["dt_txt"].split()[0]].append(item)
            else:
                grouped[item["dt_txt"].split()[0]] = [item]

            item["dt_txt"].split()[0]

    # def __str__(self):
    #     return f"---------------\ndt: {self.unixToUTC(self.today["dt"])}\nTemp: {self.kelvinToCelcius(self.today["temp"])}\nFeels like: {self.kelvinToCelcius(self.today["feels_like"])}\n---------------"


# url = BASE_URL + WEATHER + "appid=" + API_KEY + "&q=SS6"


def writeWeather(url):
    r = requests.get(url).json()
    with open("weather2.json", "w") as f:
        json.dump(r, f)


# app = WeatherObject()
# print(app.today["main"]["temp"])
# dateList = []
# for item in app.list:
#     dateList.append(app.unixToUTC(item["dt"]))
# indexes = indexOfTimes(dateList, 22)
# print(indexes)

# for i in range(2, len(app.list), 8):

#     print(i+1, app.unixToUTC(app.list[i]["dt"]).hour)
# print(app.unixToUTC(app.list[-1]["dt"])-app.unixToUTC(app.list[0]["dt"]))
