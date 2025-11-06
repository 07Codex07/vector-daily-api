# check_db.py
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "subscribers.db")

if not os.path.exists(DB_PATH):
    print("❌ Database not found at:", DB_PATH)
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT * FROM subscribers;")
rows = cursor.fetchall()

if not rows:
    print("⚠️ No subscribers found.")
else:
    print("✅ Subscribers in database:")
    for row in rows:
        print(row)

conn.close()
