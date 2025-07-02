# from weatherapp import WeatherObject
from flask import Flask

app = Flask(__name__)

@app.route("/")
def test():
    return "Hello"

@app.route("/testing")
def printing():
    return "This is the testing side"

app.run(host="0.0.0.0", port=80)
