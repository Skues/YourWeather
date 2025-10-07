from . import sleepBP
from flask import render_template, redirect, session, url_for, request
from ..models.database import databaseConnection
from ..models.weatherapp import WeatherObject
from ..constants.constants import PREFERENCES

weatherApp = WeatherObject()

dbConn = databaseConnection()
db = dbConn.db
cursor = db.cursor()


@sleepBP.route("/sleep")
def sleepPreference():
    # Check to see if the user has a preference set
    # and use the preferene against the actual weather forecast to see
    # if they will sleep well tonight and some nights in the future
    username = session.get("username")
    print(username)
    if username is None:
        return render_template(
            "account.html", error="Must have an account to see how you will sleep."
        )
    sql = "SELECT p.heat, w.location from preferences as p join WeatherData as w on p.userID = w.userID where p.userID = %s"
    cursor.execute(sql, [session.get("id")])
    result = cursor.fetchone()
    if not result:
        return "No user found"
    preference = result[0]
    location = result[1]
    weatherApp.setLocation("forecast", location)

    sleepData = []
    indexes = weatherApp.indexOfTimes(weatherApp.list["list"], 22)
    tempRange = PREFERENCES[preference.lower()]
    for index in indexes:
        data = weatherApp.list["list"][index]
        sleepDict = {
            "date": data["dt_txt"],
            "temp": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "weatherType": data["weather"][0]["description"],
            "cloudCover": data["clouds"]["all"],
            "windSpeed": data["wind"]["speed"],
        }
        if "rain" in data:
            sleepDict["rain"] = data["rain"]["3h"]
        sleepData.append(sleepDict)

    # Get wind speed, humidity, air quality?

    return render_template(
        "sleep.html",
        list=weatherApp.list,
        indexes=indexes,
        sleepData=sleepData,
    )
