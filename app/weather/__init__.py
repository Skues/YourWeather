from flask import Blueprint

weatherBP = Blueprint("weather", __name__, template_folder="templates")

from . import routes
