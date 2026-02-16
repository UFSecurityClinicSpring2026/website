import sqlite3

import flask

import sqldb

app: flask.Flask = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.render_template("index.html")

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