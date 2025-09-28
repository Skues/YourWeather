from flask import Blueprint

mainBP = Blueprint("main", __name__, template_folder="templates")

from . import routes
