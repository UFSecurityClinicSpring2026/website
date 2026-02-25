"""
Custom User class for use with flask_login
"""
import sqldb
import werkzeug.security as wk

class User:
  def __init__(self, username, name, is_client, is_student):
    self._username = username
    self._name = name
    self._is_client = is_client
    self._is_student = is_student
    self._authenticated = True
    self._active = True
    self._anonymous = False
  
  def check(username):
    sql_db: sqlite3.Connection = sqldb.get_db()
    res = sql_db.execute("SELECT username, first_name, last_name, is_client, is_student FROM users WHERE username = ?;", (username,)).fetchall()
    if len(res) == 0:
      return None
    return User(res[0][0], res[0][1] + " " + res[0][2], res[0][3], res[0][4])

  @property
  def is_authenticated(self):
    return self._authenticated
  
  @property
  def is_active(self):
    return self._active
  
  @property
  def is_anonymous(self):
    return self._anonymous

  def deactivate(self):
    self._active = False
  
  def authenticate(self):
    self._authenticated = True
  
  def get_id(self):
    return self._username