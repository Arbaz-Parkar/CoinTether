# src/gui.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt

class CoinTetherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CoinTether - Login")
        self.setGeometry(100, 100, 400, 300)
        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # --- Title ---
        title = QLabel("CoinTether Login")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        # --- Username ---
        username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")

        # --- Password ---
        password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter password")

        # --- Role Selection ---
        role_label = QLabel("Login as:")
        self.role_select = QComboBox()
        self.role_select.addItems(["User", "Admin"])

        # --- Login Button ---
        login_button = QPushButton("Login")
        login_button.clicked.connect(self.handle_login)

        # --- Layout ---
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(role_label)
        layout.addWidget(self.role_select)
        layout.addWidget(login_button)

        central_widget.setLayout(layout)

    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        role = self.role_select.currentText()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        # Placeholder: actual validation logic will come later
        QMessageBox.information(self, "Login", f"Welcome {role}: {username}")
