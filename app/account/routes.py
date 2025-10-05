from . import accountBP

from flask import redirect, render_template, session, url_for, request

from ..models.database import databaseConnection

dbConn = databaseConnection()
db = dbConn.db
cursor = db.cursor()


@accountBP.route("/account")
def account():
    error = ""
    loggedIn = False
    username = session.get("username")
    if username is not None:
        loggedIn = True
        sql = f"SELECT preferences.heat, WeatherData.location from preferences join WeatherData on preferences.userID = WeatherData.userID where preferences.userID ={session.get("id")}"
        cursor.execute(sql)
        result = cursor.fetchone()
        locationPreference, heatPreference = result[1], result[0]

        return render_template(
            "account.html",
            loggedIn=loggedIn,
            locationPreference=locationPreference,
            heatPreference=heatPreference,
            error=error,
        )

    return render_template("account.html", error=error)


@accountBP.route("/setPreferences")
def weather():
    return render_template("setPreferences.html")


@accountBP.route("/submitWeather", methods=["POST"])
def submitWeather():
    global user
    username = session.get("username")
    if username is None:
        return redirect(url_for("account"))
    location = request.form["location"]
    preference = request.form["preference"]
    # check if location is supported by api
    sql = f"INSERT INTO WeatherData (userID, location) VALUES ({session.get("id")}, '{location}')"
    cursor.execute(sql)
    db.commit()
    sql = f"INSERT INTO preferences (userID, heat) VALUES ({session.get("id")}, '{preference.title()}')"
    cursor.execute(sql)
    db.commit()
    session["location"] = location
    session["preference"] = preference
    return redirect(url_for("index"))


@accountBP.route("/changePreferences", methods=["POST", "GET"])
def changePreferences():
    if request.method == "POST":
        newLocation = request.form["newLocation"]
        newHeat = request.form["heatPreference"]
        if newLocation != "":
            # set it
            sql = f"UPDATE WeatherData SET location='{newLocation}' WHERE userID={session.get("id")}"
            cursor.execute(sql)
        if newHeat != "":
            # set it
            sql = f"UPDATE preferences set heat='{newHeat}' WHERE userID={session.get("id")}"
            cursor.execute(sql)
        db.commit()
        return redirect(url_for("account"))
    else:
        return render_template("changePreferences.html")
