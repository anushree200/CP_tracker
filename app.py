from flask import Flask, render_template
import sqlite3
app = Flask(__name__)
@app.route('/')
def frontpage():
    conn = sqlite3.connect("problems.db")
    cur = conn.cursor()
    cur.execute("SELECT * from problems")
    problems = cur.fetchall()
    conn.close()
    return render_template("problemspage.html",problems=problems)
