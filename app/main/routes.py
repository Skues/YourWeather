from flask import render_template
from . import mainBP


@mainBP.route("/")
def index():
    return render_template("index.html")
