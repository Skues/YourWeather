from flask import Flask
from .auth import authBP
from .weather import weatherBP
from .account import accountBP
from .sleep import sleepBP
from .main import mainBP
from .models.bcrypt import bcrypt
import secrets
import logging


def createApp():
    logging.basicConfig(
        level=logging.DEBUG,  # Or INFO in production
        format="%(levelname)s - %(asctime)s - %(message)s",
    )
    app = Flask(__name__)
    bcrypt.init_app(app)
    app.secret_key = secrets.token_bytes(16)

    app.register_blueprint(weatherBP, url_prefix="/weather")
    app.register_blueprint(authBP, url_prefix="/auth")
    app.register_blueprint(accountBP, url_prefix="/account")
    app.register_blueprint(mainBP, url_prefix="/")
    app.register_blueprint(sleepBP, url_prefix="/sleep")

    return app
