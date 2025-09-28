from flask import request, render_template, url_for, redirect, session
from . import authBP
from ..models import bcrypt
from ..models import database
from ..constants.constants import EMAIL_PREFIX
import logging

logger = logging.getLogger(__name__)

dbConnection = database.databaseConnection()
db = dbConnection.db
cursor = db.cursor()
brcyp = bcrypt.bcrypt


@authBP.route("/signup", methods=["POST"])
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
        logger.warning("Username already exists")
        return render_template("account.html", error=error)
    hashedPassword = brcyp.generate_password_hash(password).decode()
    dbConnection.insertValues(
        "users",
        ["username", "email", "password"],
        [username, email, hashedPassword],
    )
    cursor.execute(sql)
    result = cursor.fetchone()
    user = {"id": result[3], "username": result[0], "email": result[1]}
    return redirect(url_for("weather"))


@authBP.route("/login", methods=["POST"])
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
        dbPassword = result[0][2]
        if brcyp.check_password_hash(dbPassword, password):
            id = result[0][3]
            username = result[0][0]
            email = result[0][1]

            session["id"] = id
            session["username"] = username
            session["email"] = email
            print("USERNAME", session.get("username"))
        else:
            logger.warning("Password did not match")
            error = "Password did not match."
    else:
        error = "Account not found in database."
        logger.warning("Account not found in database.")

    if error != "":
        return render_template("account.html", error=error)
    else:
        return redirect(url_for("account.account"))


@authBP.route("/logout")
def logout():
    session.clear()
    global user
    user = {}
    return redirect(url_for("index"))
