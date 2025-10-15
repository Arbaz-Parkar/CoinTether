# src/welcome_screen.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import os
import sys

from src.login import UserLoginScreen
from src.register import RegisterScreen
from src.admin_login import AdminLoginScreen

class WelcomeScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Welcome - CoinTether")
        self.setFixedSize(420, 420)
        self.init_ui()
        self.apply_dark_theme()

    def init_ui(self):
        layout = QVBoxLayout()

        # ✅ CoinTether Logo (larger)
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'CoinTether_Logo.png'))
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaledToHeight(160, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

        # ✅ Buttons (full width)
        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.redirect_to_register)
        layout.addWidget(register_btn)

        login_btn = QPushButton("User Login")
        login_btn.clicked.connect(self.redirect_to_login)
        layout.addWidget(login_btn)

        admin_btn = QPushButton("Admin Login")
        admin_btn.clicked.connect(self.redirect_to_admin_login)
        layout.addWidget(admin_btn)

        self.setLayout(layout)

        # ✅ App icon
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'CoinStack.ico'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: Segoe UI, sans-serif;
            }
            QPushButton {
                background-color: #27AE60;
                border: none;
                padding: 10px;
                color: white;
                font-size: 16px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2ECC71;
            }
            QLabel {
                padding: 4px;
            }
        """)

    def redirect_to_login(self):
        self.login = UserLoginScreen()
        self.login.show()
        self.close()

    def redirect_to_register(self):
        self.register = RegisterScreen()
        self.register.show()
        self.close()

    def redirect_to_admin_login(self):
        self.admin = AdminLoginScreen()
        self.admin.show()
        self.close()
