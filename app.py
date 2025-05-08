from flask import Flask, render_template,request,jsonify
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

@app.route('/filter')
def filter_prob():
    points = request.args.get('points', '')
    keywords = request.args.get('keywords', '')
    query = "SELECT * FROM problems WHERE 1=1"
    params = []

    if points:
        query += " AND points = ?"
        params.append(int(points))
    
    if keywords:
        query += " AND title LIKE ?"
        params.append(f"%{keywords}%")
    conn = sqlite3.connect("problems.db")
    cur = conn.cursor()
    cur.execute(query, params)
    problems = cur.fetchall()
    conn.close()
    problems_list = [
        {"id": p[0], "title": p[1], "description": p[2], "points": p[3]}
        for p in problems
    ]

    return jsonify(problems_list)
if __name__ == '__main__':
    app.run(debug=True)