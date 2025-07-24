from weatherapp import WeatherObject
from flask import Flask, render_template, request, redirect, url_for
from database import *
import bcrypt
app = Flask(__name__)
weatherApp = WeatherObject()
if type(weatherApp) == str:
    print("ERORR DTIME", weatherApp)
    # redirect to latest URL with the error or show the error on a seperate page and let the user press a back button which 
    # would take them back to the last URL they were on.
    render_template("error.html", error=weatherApp)
db = connectDatabase()
cursor = db.cursor()
logged = False
user = {}
forecastLocation = ""
PREFERENCES = {"cold":[10, 18], "medium": [18, 21], "hot": [21, 25]}
EMAIL_PREFIX = ["@gmail.com", "@outlook.com", "@btinternet.com", "@bootyman.com"]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/current")
def current():
    signedIn = False
    if user != {}:
        sql = f"SELECT * from WeatherData WHERE userID ={user["id"]}"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result != []:
            error = weatherApp.setLocation("today", result[2])
            if error != "":
                return render_template("error.html", error=error)

        # check if their location is set then set the location and show the current weather for that place using setLocation()
        signedIn = True
        # Search for users saved location here

    weatherApp._checkDate(weatherApp.today["dt"])
    temperature = weatherApp.kelvinToCelcius(weatherApp.today["main"]["temp"])
    feelslike = weatherApp.kelvinToCelcius(weatherApp.today["main"]["feels_like"])
    location = weatherApp.location
    
    today= weatherApp.today
    dt = weatherApp.unixToUTC(today["dt"])
    return render_template("weather.html", today=today, temperature=temperature, feelslike=feelslike, signedIn = signedIn, user=user, dt=dt, location=location)

@app.route("/testing")
def printing():
    return render_template("index.html")

@app.route("/forecast", methods=["POST", "GET"])
def forecast():
    error = ""
    location = ""
    forecastList = []
    indexes = []
    global forecastLocation
    if request.method == "POST":
        location = request.form["locationInp"]
        weatherApp.setLocation("forecast", location)
        if error != "":
            return render_template("error.html", error = error)
        forecastList = weatherApp.list
        indexes = weatherApp.indexOfTimes(forecastList["list"], 22)
        forecastLocation = location

    elif user != {}:
        sql = f"SELECT location from WeatherData where userID = {user['id']}"
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            forecastLocation = result[0]
    else:
        forecastLocation = weatherApp.location
        
    weatherApp.setLocation("forecast", forecastLocation)
    forecastList = weatherApp.list
    indexes = weatherApp.indexOfTimes(forecastList["list"], 22)
    
    
    # if forecastLocation == "":
    #     return render_template("forecast.html", forecastSet = False)
    # location = request.form["locationInp"]
    # print(location)
    # weatherApp.setLocation("forecast", location)
    # forecastList = weatherApp.list
    # indexes = weatherApp.indexOfTimes(forecastList["list"], 22)
    # print(indexes)
    return render_template("forecast.html", list = forecastList, indexes = indexes, error = error)

@app.route("/signup", methods=["POST"])
def signup():
    global user
    username = request.form["signup_username"]
    email = request.form["signup_email"]
    index = email.index("@")
    if email[index:] not in EMAIL_PREFIX:
        error = "Invalid email type submitted."
        return render_template("account.html", error=error)
    password = request.form["signup_password"]
    sql = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) > 0:
        error = "Username already exists"
        print("Username already exists")
        return render_template("account.html", error = error)
    hashedPassword = hashPassword(password)
    insertValues(db, "users", ["username", "email", "password"], [username, email, hashedPassword])
    cursor.execute(sql)
    result = cursor.fetchone()
    user = {"id": result[3], "username": result[0], "email": result[1]}

    return redirect(url_for("weather"))


@app.route("/login", methods=["POST"])
def login():
    global user
    error = ""
    username_email = request.form["username_email"]
    password = request.form["login_password"]
    if "@" in username_email:
        index = username_email.index("@")
        if username_email[index:] in EMAIL_PREFIX:
            sql = f"SELECT * FROM users WHERE email = '{username_email}'"
        else:
            error = "Not a valid email address"
            return render_template("account.html", error=error)
    else:
        sql = f"SELECT * FROM users WHERE username = '{username_email}'"
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 1:
        dbPassword = hashPassword(result[0][2])
        if password == dbPassword:
            id = result[0][3]
            username = result[0][0]
            email = result[0][1]
            user = {"id": id, "username": username, "email": email}
        else:
            error = "Password did not match."
    else:
        error = "Account not found in database."
        
    if error != "":
        return render_template("account.html", error = error)
    else:
        return redirect(url_for("account"))


@app.route("/account")
def account():
    
    error = ""
    loggedIn = False
    if user != {}:
        loggedIn = True
        sql = f"SELECT preferences.heat, WeatherData.location from preferences join WeatherData on preferences.userID = WeatherData.userID where preferences.userID ={user["id"]}"
        cursor.execute(sql)
        result = cursor.fetchone()
        locationPreference, heatPreference = result[1], result[0]
        
        return render_template("account.html", loggedIn=loggedIn, locationPreference=locationPreference, heatPreference=heatPreference, error=error)

    return render_template("account.html", error=error)

@app.route("/logout")
def logout():
    global user
    user = {}
    return redirect(url_for("index"))

@app.route("/weather")
def weather():
    return render_template("weathersubmit.html")

@app.route("/submitWeather", methods=["POST"])
def submitWeather():
    global user
    if user == {}:
        return redirect(url_for("account"))
    location = request.form["location"]
    preference = request.form["preference"]
    # check if location is supported by api
    sql = f"INSERT INTO WeatherData (userID, location) VALUES ({user["id"]}, '{location}')"
    cursor.execute(sql)
    db.commit()
    sql = f"INSERT INTO preferences (userID, heat) VALUES ({user["id"]}, '{preference}')"
    cursor.execute(sql)
    db.commit()

    user["location"] = location
    user["preference"] = preference
    return redirect(url_for("index"))

@app.route("/sleep")
def sleepPreference():
    # Check to see if the user has a preference set 
    # and use the preferene against the actual weather forecast to see 
    # if they will sleep well tonight and some nights in the future
    global user
    if user == {}:
        return redirect(url_for("account"))
    sql = f"SELECT p.heat, w.location from preferences as p join WeatherData as w on p.userID = w.userID where p.userID ={user["id"]}"
    
    cursor.execute(sql)
    result = cursor.fetchone()
    if not result:
        return "No user found"
    preference = result[0]
    location = result[1]
    weatherApp.setLocation("forecast", location)

    indexes = weatherApp.indexOfTimes(weatherApp.list["list"], 22)
    tempRange = PREFERENCES[preference.lower()]
    for i in indexes:

        temp = weatherApp.list["list"][i]["main"]["feels_like"]
        if temp in range(tempRange[0], tempRange[1]+1):
            weatherApp.list["list"][i]["main"]["sleep"] = True
        else:
            weatherApp.list["list"][i]["main"]["sleep"] = False
    return render_template("sleep.html", list = weatherApp.list, indexes = indexes)

    # create another function to check the temperature versus the users preference

@app.route("/changePreferences", methods=["POST", "GET"])
def changePreferences():
    
    if request.method == "POST":
        newLocation = request.form["newLocation"]
        newHeat = request.form["heatPreference"]
        if newLocation != "":
            # set it
            sql = f"UPDATE WeatherData SET location='{newLocation}' WHERE userID={user["id"]}"
            cursor.execute(sql)

        if newHeat != "":
            # set it
            sql = f"UPDATE preferences set heat='{newHeat}' WHERE userID={user["id"]}"
            cursor.execute(sql)

        db.commit()
        return redirect(url_for("account"))
    else:
        return render_template("changePreferences.html")


def hashPassword(password: str) -> str:
    password_bytes = password.encode('utf-8')
    hashedPassword = bcrypt.hashpw(password_bytes, bcrypt.gensalt(12))
    return hashedPassword.decode('utf-8')

app.run(host="0.0.0.0", port=5000, debug=True)

