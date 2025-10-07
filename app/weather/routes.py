import logging
from flask import flash, request, render_template, url_for, redirect, session
from . import weatherBP
from ..models.weatherapp import LocationException, WeatherObject
from ..models.database import databaseConnection
import secrets
from ..constants.constants import DEFAULT_LOCATION
from app import weather

secretKey = secrets.token_bytes(16)
dbConn = databaseConnection()
db = dbConn.db
cursor = db.cursor()

weatherApp = WeatherObject()


@weatherBP.route("/current", methods=["POST", "GET"])
def current():
    signedIn = False
    today = ""
    dt = ""
    locationInfo = {}
    if request.method == "POST":
        location = request.form["locationInp"]
        error = weatherApp.setLocation("today", location)
        if error != "":
            return render_template(
                "weather.html",
                today=today,
                signedIn=signedIn,
                username=session.get("username"),
                dt=dt,
                location=location,
                locationInfo=locationInfo,
            )
    else:
        username = session.get("username")
        if username is not None:
            logging.log(logging.DEBUG, "User is logged in")
            sql = "SELECT * from WeatherData WHERE userID =%s"
            cursor.execute(sql, [session.get("id")])
            result = cursor.fetchone()
            if result:
                error = weatherApp.setLocation("today", result[2])
                if error != "":
                    return render_template("error.html", error=error)

            # check if their location is set then set the location and show the current weather for that place using setLocation()
            signedIn = True

            # Search for users saved location here
        else:
            logging.log(logging.DEBUG, "User is not logged in")
    temperatures = ["temp", "feels_like", "temp_min", "temp_max"]
    for key, value in weatherApp.today["main"].items():
        if key in temperatures:
            weatherApp.today["main"][key] = weatherApp.kelvinToCelcius(value)

    weatherApp._checkDate(weatherApp.today["dt"])

    location = weatherApp.location

    today = weatherApp.today
    dt = weatherApp.unixToUTC(today["dt"])
    logging.log(logging.DEBUG, "Rendering complete page now")
    error, locationInfo = weatherApp.checkLocation(location)
    return render_template(
        "weather.html",
        today=today,
        username=session.get("username"),
        dt=dt,
        location=location,
        locationInfo=locationInfo,
        error="",
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
        error, locationInfo = weatherApp.checkLocation(location)
        if error == "":
            forecastLocation = location
        else:
            logging.log(logging.ERROR, error)
            return render_template(
                "forecast.html", list=forecastList, indexes=indexes, error=error
            )
    elif username is not None:
        try:
            sql = "SELECT location from WeatherData where userID = %s"
            cursor.execute(sql, [session.get("id")])
            result = cursor.fetchone()
            if result:
                forecastLocation = result[0]
            else:
                forecastLocation = DEFAULT_LOCATION
        except Exception as e:
            forecastLocation = DEFAULT_LOCATION
            raise (e)

    else:
        forecastLocation = DEFAULT_LOCATION

    if forecastLocation:
        forecastList, error = setLocation("forecast", forecastLocation)
        if forecastList is None:
            return render_template(
                "forecast.html", list=forecastList, indexes=indexes, error=error
            )

        indexes = weatherApp.indexOfTimes(forecastList["list"], 22)

    return render_template(
        "forecast.html", list=forecastList, indexes=indexes, error=error
    )


def setLocation(weatherType, location):
    try:
        weatherApp.setLocation(weatherType, location)
    except LocationException as e:
        return None, e
    forecastList = weatherApp.list
    error = None
    return forecastList, error
