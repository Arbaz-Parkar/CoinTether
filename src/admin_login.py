# src/admin_login.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QCheckBox
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

class AdminLoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin Login - CoinTether")
        self.setFixedSize(400, 360)

        #  App icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'coinstack_icon.ico'))
        self.setWindowIcon(QIcon(icon_path))

        self.init_ui()
        self.apply_dark_theme()

    def init_ui(self):
        layout = QVBoxLayout()

        #  Banner logo
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'CoinTether_Logo.png'))
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaledToHeight(80, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

        title = QLabel("Admin Login")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Admin Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.show_password_checkbox = QCheckBox("Show Password")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login_admin)
        layout.addWidget(login_button)

        back_button = QPushButton("Back to User Login")
        back_button.setStyleSheet("color: #5DADE2; background: transparent; border: none;")
        back_button.clicked.connect(self.redirect_to_user_login)
        layout.addWidget(back_button, alignment=Qt.AlignCenter)

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
        self.password_input.setEchoMode(
            QLineEdit.Normal if self.show_password_checkbox.isChecked() else QLineEdit.Password
        )

    def login_admin(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Both fields are required.")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            cursor.execute("SELECT password FROM admins WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()

            if result is None:
                QMessageBox.warning(self, "Login Failed", "Admin not found.")
            elif result[0] != hashed_password:
                QMessageBox.warning(self, "Login Failed", "Incorrect password.")
            else:
                from src.admin_dashboard import AdminDashboard
                self.dashboard = AdminDashboard(username)
                self.dashboard.show()
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Something went wrong:\n{str(e)}")

    def redirect_to_user_login(self):
        from src.login import UserLoginScreen
        self.login_window = UserLoginScreen()
        self.login_window.show()
        self.close()
