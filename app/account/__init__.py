from flask import Blueprint

accountBP = Blueprint("account", __name__, template_folder="templates")

from . import routes
