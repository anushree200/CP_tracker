import sqlite3
import json
conn = sqlite3.connect("admin.db")
cur = conn.cursor()
cur.execute("CREATE TABLE admin(username TEXT NOT NULL, pwd TEXT NOT NULL)")
cur.execute(
    "INSERT INTO admin(username,pwd) VALUES (?, ?)",
    ('anushree', 'admin')
)
conn.commit()
conn.close()