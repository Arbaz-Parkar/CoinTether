# src/login.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QHBoxLayout, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
import sqlite3
import hashlib
import os
import sys
from src.dashboard import UserDashboard

def get_database_path():
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(app_dir, 'data', 'users.db')

db_path = get_database_path()

class UserLoginScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("User Login - CoinTether")
        self.setFixedSize(420, 420)

        
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

        title = QLabel("User Login")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.show_password_checkbox = QCheckBox("Show Password")
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_password_checkbox)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.login_user)
        layout.addWidget(self.login_button)

        register_layout = QHBoxLayout()
        register_label = QLabel("Don't have an account?")
        register_button = QPushButton("Register")
        register_button.setStyleSheet("color: #5DADE2; background: transparent; border: none;")
        register_button.clicked.connect(self.redirect_to_register)
        register_layout.addWidget(register_label)
        register_layout.addWidget(register_button)
        layout.addLayout(register_layout)

        admin_button = QPushButton("Admin Login")
        admin_button.setStyleSheet("color: #E74C3C; background: transparent; border: none;")
        admin_button.clicked.connect(self.redirect_to_admin_login)
        layout.addWidget(admin_button, alignment=Qt.AlignCenter)

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

    def login_user(self):
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Both fields are required.")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            conn.close()

            if result is None:
                QMessageBox.warning(self, "Login Failed", "User not found.")
            elif result[0] != hashed_password:
                QMessageBox.warning(self, "Login Failed", "Incorrect password.")
            else:
                self.dashboard = UserDashboard(username)
                self.dashboard.show()
                self.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Something went wrong:\n{str(e)}")

    def redirect_to_register(self):
        from src.register import RegisterScreen
        self.register_window = RegisterScreen()
        self.register_window.show()
        self.close()

    def redirect_to_admin_login(self):
        from src.admin_login import AdminLoginScreen
        self.admin_window = AdminLoginScreen()
        self.admin_window.show()
        self.close()
