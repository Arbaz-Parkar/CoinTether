# create_admin.py

import sqlite3
import hashlib
import os

# Build the database path
db_path = os.path.join("data", "users.db")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create the admins table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
""")

# Choose your admin credentials
username = "arbaz"
password = "arbaz2004"

# Hash the password
hashed = hashlib.sha256(password.encode()).hexdigest()

try:
    cursor.execute("INSERT INTO admins (username, password) VALUES (?, ?)", (username, hashed))
    print("Admin created successfully.")
except sqlite3.IntegrityError:
    print("Admin already exists.")

conn.commit()
conn.close()
