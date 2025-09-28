from flask import Blueprint

authBP = Blueprint("auth", __name__, template_folder="templates")

from . import routes
