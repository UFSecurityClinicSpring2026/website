import argparse
import csv
import pathlib
import sqlite3
import sys
import typing

def main(argv: list[str]) -> int:
    argparser: argparse.ArgumentParser = argparse.ArgumentParser()
    argparser.add_argument("in_file", type=pathlib.Path,
            help="Input CSV to import questions from.")
    parsedargs: dict[str, typing.Any] = vars(argparser.parse_args(argv[1:]))
    database: sqlite3.Connection = sqlite3.connect("exam.db")
    
    question_insert_query: str = '''INSERT INTO question 
    (fid, question, correct, incorrect1, incorrect2, incorrect3, incorrect4)
    VALUES (?, ?, ?, ?, ?, ?, ?) ON CONFLICT DO UPDATE 
    SET question=excluded.question, correct=excluded.correct, incorrect1=excluded.incorrect1,
    incorrect2=excluded.incorrect2, incorrect3=excluded.incorrect3, incorrect4=excluded.incorrect4;
    '''
    
    database.execute("CREATE TABLE IF NOT EXISTS \"exam\" ( \"fid\" INTEGER NOT NULL, \"token\" TEXT NOT NULL UNIQUE, \"fname\" TEXT NOT NULL, \"lname\" TEXT NOT NULL, \"password\" TEXT NOT NULL, \"starttime\" INTEGER, \"endtime\" INTEGER, PRIMARY KEY(\"fid\" AUTOINCREMENT));")
    database.execute('''CREATE TABLE IF NOT EXISTS \"examquestion\" (
        \"fid\" INTEGER NOT NULL,
        \"examfid\" INTEGER NOT NULL,
        \"questionid\" INTEGER NOT NULL,
        \"answerorder\" INTEGER NOT NULL,
        \"score\" INTEGER,
        PRIMARY KEY(\"fid\" AUTOINCREMENT),
        FOREIGN KEY(\"examfid\") REFERENCES \"question\"(\"fid\") ON UPDATE CASCADE ON DELETE RESTRICT
    );''')
    database.execute("CREATE TABLE IF NOT EXISTS \"question\" ( \"fid\" INTEGER NOT NULL, \"question\" TEXT NOT NULL, \"correct\" TEXT NOT NULL, \"incorrect1\" TEXT NOT NULL, \"incorrect2\" TEXT, \"incorrect3\" TEXT, \"incorrect4\" TEXT, PRIMARY KEY(\"fid\" AUTOINCREMENT));")
    database.commit()
    
    with open(parsedargs["in_file"], 'r', newline="") as questions_csv_file:
        questions_csv: csv.DictReader = csv.DictReader(questions_csv_file)
        for question_row in questions_csv:
            ans_incorrect_2: typing.Optional[str] = question_row["incorrect2"]
            ans_incorrect_3: typing.Optional[str] = question_row["incorrect3"]
            ans_incorrect_4: typing.Optional[str] = question_row["incorrect4"]
            if ans_incorrect_2 is not None and ans_incorrect_2.strip() == "":
                ans_incorrect_2 = None
            if ans_incorrect_3 is not None and ans_incorrect_3.strip() == "":
                ans_incorrect_3 = None
            if ans_incorrect_4 is not None and ans_incorrect_4.strip() == "":
                ans_incorrect_4 = None
            database.execute(question_insert_query, (
                question_row["questionid"],
                question_row["question"],
                question_row["correct"],
                question_row["incorrect1"],
                ans_incorrect_2,
                ans_incorrect_3,
                ans_incorrect_4,
            ))
    
    database.commit()
    
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))