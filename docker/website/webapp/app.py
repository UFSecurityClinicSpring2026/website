import sqlite3

import flask

import sqldb

import werkzeug.security as wk

import re

from user import User

import flask_login

app: flask.Flask = flask.Flask(__name__)
app.secret_key = "super secret string" # CHANGE THIS FOR PRODUCTION
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

"""
Overloading function for LoginManager
"""
@login_manager.user_loader
def user_loader(username):
  return User.check(username)

def check_requirements(username: str, password: str):
  return re.match(".{15,64}", password) is not None and re.match("\\w+", username) is not None

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/contact")
def contact_us():
    return flask.render_template("contact.html")

@app.route("/about")
def about_us():
    return flask.render_template("about.html")

@app.route("/privacy")
def privacy_policy():
    return flask.render_template("privacy-policy.html")

@app.route("/tickets/new", methods=["GET", "POST"])
def new_ticket():
    if flask.request.method == "GET":
        return flask.render_template("new-ticket-form.html")
    elif flask.request.method == "POST":
        sql_db: sqlite3.Connection = sqldb.get_db()
        if "name" not in flask.request.form or "email" not in flask.request.form or \
                "message" not in flask.request.form:
            flask.abort(422)
        sql_db.execute("INSERT INTO tickets (name, email, message) VALUES (?, ?, ?);",
                (flask.request.form["name"], flask.request.form["email"],
                flask.request.form["message"],))
        sql_db.commit()
        return flask.render_template(
            "delayed-redirect.html", 
            title="Ticket submitted!", 
            delay=5,
            message="We've received your response and will reply to it " + 
                    "within 3-5 business days.",
            destination="/",
        )
    else:
        flask.abort(405)

@app.route("/register", methods=["GET", "POST"])
def register():
    if flask.request.method == "GET":
        return flask.render_template("register.html")
    elif flask.request.method == "POST":
        sql_db: sqlite3.Connection = sqldb.get_db()
        if "username" not in flask.request.form or "first_name" not in flask.request.form or \
                "last_name" not in flask.request.form or "password" not in flask.request.form or \
                "selection" not in flask.request.form:
            flask.abort(422)
        username, password = flask.request.form["username"].strip(), flask.request.form["password"].strip()
        is_client = 0
        is_student = 0
        if flask.request.form["selection"] == "client":
            is_client = 1
        elif flask.request.form["selection"] == "student":
            is_student = 1
        else:
            print("bad selection")
            flask.abort(422)
        if not check_requirements(username, password):
          # Should have a check in frontend as well, but okay for now
            flask.abort(422)
        hashed = wk.generate_password_hash(password, salt_length=32)
        res = sql_db.execute("SELECT username FROM users WHERE username = ?;", (username,))
        res = res.fetchall()
        if len(res) > 0:
            flask.abort(422)
        sql_db.execute("INSERT INTO users (username, first_name, last_name, auth_string, is_student, is_client) VALUES (?, ?, ?, ?, ?, ?);", \
                        (username, flask.request.form["first_name"], flask.request.form["last_name"], \
                         hashed, is_student, is_client))
        sql_db.commit()
        return flask.render_template(
            "delayed-redirect.html",
            title="Registered Successfully!",
            delay=5,
            message="You have successfully registered as a " + flask.request.form["selection"],
            destination="/"
        )
    else:
        flask.abort(405)

@app.route("/login", methods=["GET", "POST"])
def login():
    if flask.request.method == "GET":
        return flask.render_template("login.html")
    elif flask.request.method == "POST":
        sql_db: sqlite3.Connection = sqldb.get_db()
        if "username" not in flask.request.form or "password" not in flask.request.form:
            flask.abort(422)
        username, password = flask.request.form["username"].strip(), flask.request.form["password"].strip()
        if re.match("\\w+", username) is None:
            flask.abort(422)
        res = sql_db.execute("SELECT username, auth_string, first_name, last_name, is_student, is_client FROM users WHERE username = ?;", (username,)).fetchall()
        if len(res) == 0:
            flask.abort(401)
        pass_hash = res[0][1]
        first_name = res[0][2]
        last_name = res[0][3]
        is_student = res[0][4]
        is_client = res[0][5]
        if not wk.check_password_hash(pass_hash, password):
            flask.abort(401)
        user = User(username, first_name + " " + last_name, is_client, is_student)
        flask_login.login_user(user)
        return flask.redirect('/')
    else:
        flask.abort(405)

@app.route("/test-login", methods=["GET"])
@flask_login.login_required
def test():
  return "Logged in as " + flask_login.current_user.get_id()

@app.route("/logout", methods=["GET", "POST"])
@flask_login.login_required
def logout():
  flask_login.logout_user()
  return flask.redirect('/')