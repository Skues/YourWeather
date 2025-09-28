from flask import flash, request, render_template, url_for, redirect, session
from . import weatherBP
from ..models.weatherapp import WeatherObject
from ..models.database import databaseConnection
import secrets
from ..constants.constants import DEFAULT_LOCATION

secretKey = secrets.token_bytes(16)
dbConn = databaseConnection()
db = dbConn.db
cursor = db.cursor()

weatherApp = WeatherObject()


@weatherBP.route("/current", methods=["POST", "GET"])
def current():
    signedIn = False
    if request.method == "POST":
        location = request.form["locationInp"]
        error = weatherApp.setLocation("today", location)
        if error != "":
            flash(error)
            return render_template("error.html", error=error)
    else:
        username = session.get("username")
        if username is not None:
            sql = f"SELECT * from WeatherData WHERE userID ={session.get("id")}"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                error = weatherApp.setLocation("today", result[2])
                if error != "":
                    return render_template("error.html", error=error)

            # check if their location is set then set the location and show the current weather for that place using setLocation()
            signedIn = True
            # Search for users saved location here
    temperatures = ["temp", "feels_like", "temp_min", "temp_max"]
    for key, value in weatherApp.today["main"].items():
        if key in temperatures:
            weatherApp.today["main"][key] = weatherApp.kelvinToCelcius(value)

    weatherApp._checkDate(weatherApp.today["dt"])

    location = weatherApp.location

    today = weatherApp.today
    dt = weatherApp.unixToUTC(today["dt"])
    return render_template(
        "weather.html",
        today=today,
        signedIn=signedIn,
        username=session.get("username"),
        dt=dt,
        location=location,
    )


@weatherBP.route("/forecast", methods=["POST", "GET"])
def forecast():
    error = ""
    location = ""
    forecastList = []
    indexes = []
    username = session.get("username")
    id = session.get("id")
    if request.method == "POST":
        location = request.form["locationInp"]
        forecastLocation = location
        # check if location is valid
    elif username is not None:
        try:
            sql = f"SELECT location from WeatherData where userID = {session.get("id")}"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                forecastLocation = result[0]
            else:
                forecastLocation = DEFAULT_LOCATION
        except Exception as e:
            raise (e)
            forecastLocation = DEFAULT_LOCATION

    else:
        forecastLocation = DEFAULT_LOCATION

    if forecastLocation:
        forecastList, indexes = setLocation("forecast", forecastLocation)
    return render_template(
        "forecast.html", list=forecastList, indexes=indexes, error=error
    )


def setLocation(type, location):
    error = weatherApp.setLocation(type, location)
    if error != "":
        return render_template("error.html", error=error)
    forecastList = weatherApp.list
    indexes = weatherApp.indexOfTimes(forecastList["list"], 22)
    return forecastList, indexes
