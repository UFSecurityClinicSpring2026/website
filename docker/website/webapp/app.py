import sqlite3

import flask

import sqldb

import werkzeug.security as wk

import re

from user import User

import flask_login

import forms

import uploads

import flask_mail

import dotenv

import os

import jwt

from time import time

dotenv.load_dotenv()
app: flask.Flask = flask.Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY') # CHANGE THIS FOR PRODUCTION
app.config['MAX_CONTENT_LENGTH'] = uploads.max_filesize
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT')) 
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS') == 'True'
app.config['MAIL_USE_SSL'] = os.getenv('MAIL_USE_SSL') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = flask_mail.Mail(app)

"""
Overloading function for LoginManager
"""
@login_manager.user_loader
def user_loader(username):
  return User.retrieve(username)

def check_requirements(username: str, password: str):
  return re.match(".{15,64}", password) is not None and re.match("\\w+", username) is not None

def send_verification_email(name, email, username):
  token = jwt.encode({'verify_email': username, 'exp': time() + 60*60}, app.secret_key, algorithm='HS256')
  msg = flask_mail.Message(subject='[Florida Security Clinic] Verification Email',
                           recipients=[email],
                           body=flask.render_template('verify.txt', token=token, user=name))
  
  try:
    mail.send(msg)
    return True
  except Exception as e:
    print(f"Error sending verification email: {str(e)}")
    return False


@app.route("/")
def index():
    return flask.render_template("index.html")

@app.route("/contact", methods=["GET", "POST"])
def contact_us():
    if flask.request.method == "GET":
        return flask.render_template("contact.html")
    elif flask.request.method == "POST":
        '''
        org_name = form.org_name.data
        org_description = form.org_description.data
        it_staff = form.it_staff.data
        extra_org_info = form.extra_org_info.data
        poc_name = form.poc_name.data
        poc_title = form.poc_title.data
        poc_email = form.poc_email.data
        poc_phone = form.poc_phone.data
        '''
        
        sql_db: sqlite3.Connection = sqldb.get_db()
        sql_db.execute("INSERT INTO contact (orgname, orgdescription, " + 
                "orgextra, pocname, pocemail, pocphone) " + 
                "VALUES (?, ?, ?, ?, ?, ?);", (
            flask.request.form.get("orgname", None),
            flask.request.form.get("orgdescription", None),
            flask.request.form.get("orgextra", None),
            flask.request.form.get("pocname", None),
            flask.request.form.get("pocemail", None),
            flask.request.form.get("pocphone", None),
        ))
        sql_db.commit()
        
        return flask.render_template(
            "delayed-redirect.html", 
            title="Thanks for reaching out!", 
            delay=5,
            message="Thanks for reaching out! We'll get back to you as soon as possible.",
            destination="/",
        )
    else:
        flask.abort(405)
    

@app.route("/about")
def about_us():
    return flask.render_template("about.html")

@app.route("/expect")
def what_to_expect():
    return flask.render_template("whattoexpect.html")

@app.route("/privacy")
def privacy_policy():
    return flask.render_template("privacy-policy.html")

@app.route("/tickets/new", methods=["GET", "POST"])
@flask_login.login_required
def new_ticket():
    if flask.request.method == "GET":
        return flask.render_template("new-ticket-form.html")
    elif flask.request.method == "POST":
        sql_db: sqlite3.Connection = sqldb.get_db()
        cursor = sql_db.cursor()
        if "title" not in flask.request.form or "message" not in flask.request.form:
            flask.abort(422)
        cursor.execute("INSERT INTO tickets (title, message, status, claimed) VALUES (?, ?, 1, 0);",
                (flask.request.form["title"], flask.request.form["message"],))
        cursor.execute("INSERT INTO users_tickets (uid, fid) VALUES (?, ?);", (flask_login.current_user.get_id(), cursor.lastrowid))
        sql_db.commit()
        flask.flash('Ticket Successfully Submitted', 'success')
        return flask.redirect("/tickets/dashboard")
    else:
        flask.abort(405)

@app.route("/register", methods=["GET", "POST"])
def register():
    form = forms.RegisterForm()
    valid = form.validate_on_submit()
    if flask.request.method == "GET":
        return flask.render_template("register.html", form=form)
    elif flask.request.method == "POST":
        sql_db: sqlite3.Connection = sqldb.get_db()
        if not valid:
            for _, msg in form.errors.items():
                flask.flash(msg[0], "error")
            return flask.render_template("register.html", form=form)
        username = form.username.data.strip()
        password = form.password.data.strip()
        email = form.email.data.strip()
        first_name = form.first_name.data.strip()
        last_name = form.last_name.data.strip()
        is_client = 0
        is_student = 0
        if form.selection.data == "client":
            is_client = 1
        elif form.selection.data == "student":
            is_student = 1
        else:
            is_student = 1
        if re.match("\\w+", username) is None:
            flask.flash("Username must only contain alphanumeric characters or underscores", "error")
            return flask.redirect(flask.request.url)
        hashed = wk.generate_password_hash(password, salt_length=32)
        res = sql_db.execute("SELECT username FROM users WHERE username = ?;", (username,))
        res = res.fetchall()
        if len(res) > 0:
            flask.flash("Username is unavailable", "error")
            return flask.redirect(flask.request.url)
        res = sql_db.execute("SELECT email FROM users WHERE email = ?;", (email,))
        res = res.fetchall()
        if len(res) > 0:
            flask.flash("Email is already in use", "error")
            return flask.redirect(flask.request.url)
        if not (send_verification_email(first_name + " " + last_name, email, username)):
            flask.flash("Error sending verification email. Contact clinic volunteers", "error")
            return flask.redirect(flask.request.url)
           
        sql_db.execute("INSERT INTO users (username, first_name, last_name, email, auth_string, is_student, is_client) VALUES (?, ?, ?, ?, ?, ?, ?);", \
                        (username, first_name, last_name, email, hashed, is_student, is_client))
        sql_db.commit()

        flask.flash("Registered Successfully!", "success")
        flask.flash("Please verify your email address using the link sent to your email", "info")
        flask_login.logout_user()
        return flask.redirect("/")
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
        res = sql_db.execute("SELECT uid, auth_string, first_name, last_name, is_student, is_client, email, email_verify FROM users WHERE username = ?;", (username,)).fetchall()
        if len(res) == 0:
            flask.abort(401)
        uid = res[0][0]
        pass_hash = res[0][1]
        first_name = res[0][2]
        last_name = res[0][3]
        is_student = res[0][4]
        is_client = res[0][5]
        email = res[0][6]
        if res[0][7] == 0:
            send_verification_email(first_name + " " + last_name, email, username)
            flask.flash("You must verify your email before logging in. Another verification email has been sent", "error")
            return flask.redirect("/login")
        if not wk.check_password_hash(pass_hash, password):
            flask.abort(401)
        user = User(uid, username, first_name + " " + last_name, is_client, is_student)
        flask_login.login_user(user)
        return flask.redirect('/')
    else:
        flask.abort(405)

@app.route("/logout", methods=["GET", "POST"])
@flask_login.login_required
def logout():
  flask_login.logout_user()
  return flask.redirect('/')

@app.route("/upload", methods=["GET", "POST"])
@flask_login.login_required
def upload():
  if flask.request.method == "GET":
    return flask.render_template("upload.html")
  if flask.request.method == "POST":
    if 'document' not in flask.request.files:
      flask.flash("No file included", "error")
      return flask.redirect(flask.request.url)
    file = flask.request.files['document']
    if file.filename == '':
      flask.flash("No file selected", "error")
      return flask.redirect(flask.request.url)
    if file and uploads.validate(file):
      file.stream.seek(0)
      original, unique = uploads.save_file(file)
      print(file.content_length)

      uid = flask_login.current_user.get_id()
      sql_db: sqlite3.Connection = sqldb.get_db()
      sql_db.execute("INSERT INTO uploads (unique_name, uid, original_name) VALUES (?, ?, ?)", (unique, uid, original,))
      sql_db.commit()

      flask.flash("File successfully uploaded!", "success")
      return flask.redirect('/upload')
    else:
      flask.flash("Invalid file type", "error")
      return flask.redirect(flask.request.url)

@app.route('/verify/<token>', methods=["GET"])
def verify_email(token):
  try:
    username = jwt.decode(token, app.secret_key, algorithms="HS256")['verify_email']
    sql_db: sqlite3.Connection = sqldb.get_db()
    res = sql_db.execute("SELECT email_verify FROM users WHERE username = ?", (username,)).fetchall()
    if len(res) != 1:
      flask.flash("Invalid user. Try registering again", "error")
      return flask.redirect("/")
    if int(res[0][0]) == 1:
      flask.flash("Email already verified", "info")
      return flask.redirect("/login")

    sql_db.execute("UPDATE users SET email_verify = 1 WHERE username = ?", (username,))
    sql_db.commit()
    flask.flash("Successfully verified email address", "success")
    return flask.redirect("/login")
  except Exception as e:
    flask.flash("Invalid verification link", "error")
    print(f"Error: {str(e)}")
    return flask.redirect("/")

@app.route('/tickets/dashboard', methods=["GET"])
@flask_login.login_required
def ticket_view():
  curr_user = flask_login.current_user
  if (curr_user.is_client()):
    sql_db: sqlite3.Connection = sqldb.get_db()
    res = sql_db.execute("SELECT title, message, status FROM tickets JOIN users_tickets ON tickets.fid = users_tickets.fid JOIN users ON users_tickets.uid = users.uid WHERE users.uid = ?;", (curr_user.get_id(),))
    print(res.fetchall())
    return flask.render_template('ticket-dashboard-client.html')
  elif (curr_user.is_student()):
    sql_db: sqlite3.Connection = sqldb.get_db()
    res = sql_db.execute("SELECT title, message, status FROM tickets JOIN claimed_tickets ON tickets.fid = claimed_tickets.fid JOIN users ON claimed_tickets.uid = users.uid WHERE users.uid = ?;", (curr_user.get_id(),))
    print("Claimed tickets: ", res.fetchall())
    res = sql_db.execute("SELECT title, message, users.first_name, users.last_name, status FROM tickets LEFT JOIN claimed_tickets ON tickets.fid = claimed_tickets.fid JOIN users_tickets ON tickets.fid = users_tickets.fid JOIN users ON users_tickets.uid = users.uid WHERE claimed_tickets.fid IS NULL;")
    print("Unclaimed tickets: ", res.fetchall())
    return flask.render_template('ticket-dashboard-student.html')