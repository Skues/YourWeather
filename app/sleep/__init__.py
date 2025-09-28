from flask import Blueprint

sleepBP = Blueprint("sleep", __name__, template_folder="templates")

from . import routes
