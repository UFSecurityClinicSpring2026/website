"""
Database handling functions for Flask.

Change the database path with the environment variable FSC_DB_PATH
"""

import sqlite3

import flask

def get_db() -> sqlite3.Connection:
    """
    Gets the SQLite database associated with this app
    """
    if "db" not in flask.g:
        flask.g.db = sqlite3.connect("exam.db")
        flask.g.db.execute("CREATE TABLE IF NOT EXISTS tickets (fid INTEGER NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL, message TEXT, PRIMARY KEY (fid AUTOINCREMENT));")
        flask.g.db.commit()
    
    return flask.g.db

def close_db():
    """
    Close the SQLite database associated with this app
    """
    db = g.pop('db', None)

    if db is not None:
        db.close()