import sqlite3
import json
conn = sqlite3.connect("problems.db")
cur = conn.cursor()
cur.execute("CREATE TABLE problems(id INTEGER PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL, points INTEGER NOT NULL, topic TEXT NOT NULL, test_inputs TEXT NOT NULL, test_outputs TEXT NOT NULL)")
cur.execute(
    "INSERT INTO problems (id, title, description, points,topic,test_inputs, test_outputs) VALUES (?, ?, ?, ?,?,?,?)",
    (1, 'Two Sum', 'Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target. You may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.', 300,'array', json.dumps(['2,7,11,15\n9','3,2,4\n6','3,3\n6']),json.dumps(['0,1','1,2','0,1']))
)
conn.commit()
conn.close()