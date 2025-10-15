# src/db.py

import sqlite3
import os

DB_PATH = "cointether.db"

def init_db():
    if not os.path.exists(DB_PATH):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    role TEXT NOT NULL CHECK (role IN ('User', 'Admin'))
                );
            """)
            print("Database initialized and 'users' table created.")
    else:
        print("Database already exists.")

def insert_dummy_user():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ("testuser", "testpass", "User")
        )
        conn.commit()
        print("Dummy user inserted successfully.")
    except sqlite3.IntegrityError:
        print("Dummy user already exists.")
    finally:
        conn.close()

def fetch_all_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role FROM users")
    rows = cursor.fetchall()
    conn.close()

    print("Current users in database:")
    for row in rows:
        print(row)

