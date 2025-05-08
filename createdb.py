import sqlite3

conn = sqlite3.connect("problems.db")
cur = conn.cursor()
cur.execute("CREATE TABLE problems(id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, points INTEGER NOT NULL)")
cur.execute(
    "INSERT INTO problems (id, title, description, points) VALUES (?, ?, ?, ?)",
    (1, 'Two Sum', 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.', 100)
)
conn.commit()
conn.close()