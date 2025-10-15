# src/register.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QHBoxLayout, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
import sqlite3
import hashlib
import os
import sys

def get_database_path():
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(app_dir, 'data', 'users.db')

db_path = get_database_path()

class RegisterScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register - CoinTether")
        self.setFixedSize(400, 480)

        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'coinstack_icon.ico'))
        self.setWindowIcon(QIcon(icon_path))

        self.init_ui()
        self.apply_dark_theme()

    def init_ui(self):
        layout = QVBoxLayout()

        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'CoinTether_Logo.png'))
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaledToHeight(80, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Full Name")
        layout.addWidget(self.name_input)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Confirm Password")
        self.confirm_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_input)

        self.show_password_checkbox = QCheckBox("Show Passwords")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)

        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.register_user)
        layout.addWidget(self.register_button)

        back_layout = QHBoxLayout()
        back_button = QPushButton("Back to Login")
        back_button.setStyleSheet("color: #5DADE2; background: transparent; border: none;")
        back_button.clicked.connect(self.redirect_to_login)
        back_layout.addStretch()
        back_layout.addWidget(back_button)
        back_layout.addStretch()
        layout.addLayout(back_layout)

        self.setLayout(layout)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: Segoe UI, sans-serif;
            }
            QLineEdit {
                background-color: #2C2C2C;
                border: 1px solid #3A3A3A;
                padding: 6px;
                border-radius: 4px;
                color: #FFFFFF;
            }
            QPushButton {
                background-color: #27AE60;
                border: none;
                padding: 8px;
                color: white;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ECC71;
            }
            QCheckBox {
                padding: 4px;
            }
            QLabel {
                padding: 2px;
            }
        """)

    def toggle_password_visibility(self):
        mode = QLineEdit.Normal if self.show_password_checkbox.isChecked() else QLineEdit.Password
        self.password_input.setEchoMode(mode)
        self.confirm_input.setEchoMode(mode)

    def register_user(self):
        name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        pwd = self.password_input.text()
        confirm = self.confirm_input.text()

        if not all([name, username, email, pwd, confirm]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        if pwd != confirm:
            QMessageBox.warning(self, "Password Error", "Passwords do not match.")
            return

        hashed = hashlib.sha256(pwd.encode()).hexdigest()

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            cursor.execute(
                "INSERT INTO users (name, username, email, password) VALUES (?, ?, ?, ?)",
                (name, username, email, hashed)
            )
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Success", "Account created successfully!")
            self.redirect_to_login()

        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Username or email already exists.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Something went wrong:\n{e}")

    def redirect_to_login(self):
        from src.login import UserLoginScreen
        self.login_window = UserLoginScreen()
        self.login_window.show()
        self.close()
