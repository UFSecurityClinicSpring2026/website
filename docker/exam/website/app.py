import datetime
import os
import random
import sqlite3
import uuid

import flask

import basicauth
import lehmer
import sqldb

base_url: str = os.environ.get("BASE_URL", "")
"""The base URL at the root of the app. Include a leading slash"""

app: flask.Flask = flask.Flask(__name__, static_url_path=f"{base_url}/static")

@app.route(f"{base_url}/")
def index():
    return flask.render_template("index.html")
    
@app.route(f"{base_url}/index.html")
def index_html():
    return flask.render_template("index.html")

@app.route(f"{base_url}/browsercheck")
def browser_check():
    return flask.render_template("browsercheck.html")

@app.route(f"{base_url}/exam-login", methods=["GET", "POST"])
def exam_login():
    if flask.request.method == "GET":
        return flask.render_template("examlogin.html", 
                error_msg=flask.request.args.get('error', None))
    elif flask.request.method == "POST":
        exam_db: sqlite3.Connection = sqldb.get_db()
        for row in exam_db.execute("SELECT token, starttime, endtime FROM exam WHERE fname=? AND lname=? AND password=?;",
                (flask.request.form["firstname"], flask.request.form["lastname"], 
                flask.request.form["password"])):
            flask_response = flask.make_response(flask.redirect(flask.url_for("exam_main")))
            flask_response.set_cookie("token", row[0], httponly=True, max_age=86400)
            return flask_response
            break
        else:
            # User not found
            return flask.redirect(flask.url_for("exam_login", error="Invalid name or password"))
    else:
        flask.abort(405)

@app.route(f"{base_url}/exam-secure")
def exam_main():
    exam_token: typing.Optional[str] = flask.request.cookies.get("token", "")
    if exam_token.strip == "":
        return flask.redirect(flask.url_for("exam_login", error="Session expired"))
    exam_db: sqlite3.Connection = sqldb.get_db()
    if flask.request.args.get("start", "") == "yes":
        for row in exam_db.execute("SELECT starttime FROM exam WHERE token=? LIMIT 1", (exam_token,)):
            if row[0] is None:
                exam_db.execute("UPDATE exam SET starttime=? WHERE token=?", 
                        (round(datetime.datetime.now().astimezone(datetime.timezone.utc).timestamp()), exam_token,))
                exam_db.commit()
    for row in exam_db.execute("SELECT token, starttime, endtime, fname, lname " + 
            "FROM exam WHERE token=? LIMIT 1", (exam_token,)):
        if row[1] is None:
            # Exam not started
            return flask.render_template("examready.html", name=f"{row[3]} {row[4]}")
        elif row[2] is None:
            # Exam started, but not finished
            questions: list[tuple[int, str, list[tuple[int, str]]]] = []
            for row in exam_db.execute("SELECT question, answerorder, correct, " + 
                    "incorrect1, incorrect2, incorrect3, incorrect4, question.fid " + 
                    "FROM ((examquestion JOIN question ON examquestion.questionid=question.fid) JOIN " + 
                    "exam ON examquestion.examfid=exam.fid) WHERE exam.token=?", (exam_token,)):
                raw_answer_choices: list[str] = list(row[2:4])
                if row[4] is not None:
                    raw_answer_choices.append(row[4])
                if row[5] is not None:
                    raw_answer_choices.append(row[5])
                if row[6] is not None:
                    raw_answer_choices.append(row[6])
                    
                # Now permute the answer choices
                answer_permutation: lehmer.Permutation = \
                        lehmer.Permutation.from_lehmer(row[1], len(raw_answer_choices))
                answer_choices: list[str] = answer_permutation(raw_answer_choices)
                
                answer_number_choices: list[tuple[int, str]] = []
                answer_number: int = 0
                for answer_choice in answer_choices:
                    answer_number_choices.append((answer_number, answer_choice))
                    answer_number += 1
                
                questions.append((
                    row[7],  # Question ID
                    row[0],  # Question text
                    answer_number_choices,
                ))
                
            return flask.render_template("exam.html", questions=questions)
        else:
            # Exam finished. Show score instead
            score_string: str = "NaN"
            correct_answers: int = 0
            for row in exam_db.execute("SELECT SUM(examquestion.score) " + 
                    "FROM (exam JOIN examquestion ON exam.fid=examquestion.examfid) " + 
                    "WHERE exam.token=? " + 
                    "GROUP BY exam.token;", (exam_token,)):
                correct_answers = row[0]
                break
            total_answers: int = 0
            for row in exam_db.execute("SELECT COUNT(*) " + 
                    "FROM (exam JOIN examquestion ON exam.fid=examquestion.examfid) " + 
                    "WHERE exam.token=? AND examquestion.score IS NOT NULL " + 
                    "GROUP BY exam.token;", (exam_token,)):
                total_answers = row[0]
            if total_answers > 0:
                score_string = f"{correct_answers}/{total_answers} - " + \
                        f"{round(100*correct_answers/total_answers, 1)}%"
            
            examinee_name: str = ""
            exam_datetime_str: str = ""
            exam_timestamp: int = 0
            for row in exam_db.execute("SELECT fname, lname, endtime " + 
                    "FROM exam WHERE token=?", (exam_token,)):
                examinee_name = row[0] + " " + row[1]
                exam_timestamp = row[2]
                # Fallback exam date (if JavaScript disabled in browser)
                exam_datetime_str = datetime.datetime.fromtimestamp(row[2])\
                        .astimezone(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
            
            exam_passed: bool = False
            """Whether the user passed the exam"""
            if total_answers > 0:
                exam_passed = correct_answers/total_answers >= 0.7
            
            return flask.render_template("examresults.html", 
                    name=examinee_name, score=score_string, passed=exam_passed,
                    exam_timestamp=exam_timestamp, exam_datetime_fallback_str=exam_datetime_str)
    else:
        flask.abort(401)

@app.route(f"{base_url}/exam-submit", methods=["GET", "POST"])
def exam_submit():
    if flask.request.method == "POST":
        exam_token: typing.Optional[str] = flask.request.cookies.get("token", "")
        if exam_token.strip == "":
            return flask.redirect(flask.url_for("exam_login", error="Session expired"))
        exam_db: sqlite3.Connection = sqldb.get_db()
        exam_fid: typing.Optional[int] = None
        for row in exam_db.execute("SELECT fid FROM exam WHERE token=?;", (exam_token,)):
            exam_fid = row[0]
            break
        if exam_fid is None:
            # Invalid exam token, the session must have expired.
            return flask.redirect(flask.url_for("exam_login", error="Session expired"))
        
        # Update exam submit time
        exam_db.execute("UPDATE exam SET endtime=? WHERE fid=?;", (
            round(datetime.datetime.now().astimezone(datetime.timezone.utc).timestamp()),
            exam_fid,
        ))
        
        for request_form_key, request_form_value in flask.request.form.items():
            if request_form_key[0] == 'q':
                question_number: typing.Optional[int] = None
                try:
                    question_number = int(request_form_key[1:])
                except ValueError:
                    continue
                question_lehmer: typing.Optional[int] = None
                answer_choice_count: int = 2
                for row in exam_db.execute("SELECT examquestion.answerorder, " + 
                        "question.incorrect2, question.incorrect3, question.incorrect4 " +
                        "FROM (examquestion JOIN question ON examquestion.questionid=question.fid)" + 
                        "WHERE examquestion.examfid=? AND examquestion.questionid=?", 
                        (exam_fid, question_number)):
                    question_lehmer = row[0]
                    if row[1] is not None:
                        answer_choice_count += 1
                    if row[2] is not None:
                        answer_choice_count += 1
                    if row[3] is not None:
                        answer_choice_count += 1
                    break
                if question_lehmer is None:
                    # Question does not exist
                    continue
                question_permutation: lehmer.Permutation = lehmer.Permutation.from_lehmer(question_lehmer, answer_choice_count)
                
                #print("\n --- QUESTION ---")
                #print(question_permutation)
                #print(repr(request_form_value))
                
                # Mark question as correct if it equals where the correct answer would have been sorted, otherwise mark it incorrect.
                question_score: int = int(request_form_value == "a" + str(question_permutation.permutation[0]))
                exam_db.execute("UPDATE examquestion SET score=? WHERE examfid=? AND questionid=?", 
                        (question_score, exam_fid, question_number))
        exam_db.commit()
        return flask.redirect(flask.url_for("exam_main"))
    else:
        flask.abort(405)

@app.route(f"{base_url}/exam-logout")
def exam_logout():
    flask_response = flask.make_response(flask.redirect(flask.url_for("index")))
    flask_response.set_cookie("token", "", expires=0)
    return flask_response

@app.route(f"{base_url}/proctor", methods=["GET", "POST"])
@basicauth.auth_required
def proctor_portal():
    return flask.render_template("proctor.html")

@app.route(f"{base_url}/proctor-exam-create", methods=["POST"])
@basicauth.auth_required
def proctor_create_exam():
    fname: str
    lname: str
    try:
        fname = flask.request.form["firstname"]
    except KeyError:
        flask.abort(422)
    try:
        lname = flask.request.form["lastname"]
    except KeyError:
        flask.abort(422)
    
    exam_db: sqlite3.Connection = sqldb.get_db()
    exam_token: str = str(uuid.uuid4())
    gen_password: str = ""
    for _ in range(8):
        gen_password += chr(random.randint(0x61, 0x7a))
    exam_db.execute("INSERT INTO exam (token, fname, lname, password) VALUES (?, ?, ?, ?)",
            (exam_token, fname, lname, gen_password))
    exam_id: typing.Optional[int] = None
    for row in exam_db.execute("SELECT fid FROM exam WHERE token=? LIMIT 1;", (exam_token,)):
        exam_id = row[0]
        break
    assert exam_id is not None
    for row in exam_db.execute("SELECT fid FROM question ORDER BY RANDOM() LIMIT 20;"):
        exam_db.execute("INSERT INTO examquestion (examfid, questionid, answerorder) VALUES (?, ?, ?)",
                (exam_id, row[0], random.randint(0, 119)))  # Random number between 0 and 5!-1
    exam_db.commit()
    
    return flask.render_template("proctorexamshow.html", fname=fname, 
            lname=lname, password=gen_password)