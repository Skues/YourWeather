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
        sql = "SELECT preferences.heat, WeatherData.location from preferences join WeatherData on preferences.userID = WeatherData.userID where preferences.userID = %s"
        cursor.execute(sql, (session.get("id")))
        result = cursor.fetchone()
        if result is None:
            return redirect(url_for("account.setPreferences"))

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
def setPreferences():
    return render_template("setPreferences.html")


@accountBP.route("/submitPreferences", methods=["POST"])
def submitPreferences():
    username = session.get("username")
    if username is None:
        return redirect(url_for("account.account"))
    location = request.form["location"]
    preference = request.form["preference"]
    # check if location is supported by api
    sql = "INSERT INTO WeatherData (userID, location) VALUES (%s, %s)"
    cursor.execute(sql, (session.get("id"), location))
    db.commit()
    sql = "INSERT INTO preferences (userID, heat) VALUES (%s, %s)"
    cursor.execute(sql, (session.get("id"), preference.title()))
    db.commit()
    session["location"] = location
    session["preference"] = preference
    return redirect(url_for("main.index"))


@accountBP.route("/changePreferences", methods=["POST", "GET"])
def changePreferences():
    if request.method == "POST":
        newLocation = request.form["newLocation"]
        newHeat = request.form["heatPreference"]
        if newLocation != "":
            # set it
            sql = "UPDATE WeatherData SET location= %s WHERE userID= %s"
            cursor.execute(sql, (newLocation, session.get("id")))
        if newHeat != "":
            # set it
            sql = "UPDATE preferences set heat= %s WHERE userID= %s"
            cursor.execute(sql, (newHeat, session.get("id")))
        db.commit()
        return redirect(url_for("account"))
    else:
        return render_template("changePreferences.html")
