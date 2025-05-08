import sqlite3

conn = sqlite3.connect("problems.db")
cur = conn.cursor()
cur.execute("CREATE TABLE problems(id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, points INTEGER NOT NULL)")
conn.commit()
conn.close()
