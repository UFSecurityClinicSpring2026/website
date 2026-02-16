import sqlite3

import flask

import sqldb

app: flask.Flask = flask.Flask(__name__)

@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/exam/ready", methods=["GET", "POST"])
def new_ticket():
    pass
