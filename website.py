from models.weatherapp import WeatherObject
from flask import Flask, render_template, request, redirect, url_for
from models.database import databaseConnection


app = Flask(__name__)
weatherApp = WeatherObject()
if type(weatherApp) == str:

    print("ERORR DTIME", weatherApp)
    # redirect to latest URL with the error or show the error on a seperate page and let the user press a back button which
    # would take them back to the last URL they were on.
    render_template("error.html", error=weatherApp)
dbConnection = databaseConnection()
db = dbConnection.db
cursor = db.cursor()
logged = False
user = {}
forecastLocation = ""


# create another function to check the temperature versus the users preference
