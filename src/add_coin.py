# src/add_coin.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QPushButton,
    QLabel, QMessageBox, QScrollArea, QWidget, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sqlite3
import os
import sys
import requests
from io import BytesIO

from src.price_fetcher import SYMBOL_TO_ID, fetch_prices

def get_database_path():
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        return os.path.join(app_dir, 'users.db')
    else:
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        return os.path.join(app_dir, 'users.db')

db_path = get_database_path()

class AddCoinDialog(QDialog):
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("Add Coin")
        self.setFixedSize(300, 250)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.coin_name_input = QLineEdit()
        self.coin_name_input.setPlaceholderText("Coin Name (e.g., Bitcoin)")

        self.symbol_input = QLineEdit()
        self.symbol_input.setPlaceholderText("Symbol (e.g., BTC)")

        self.holdings_input = QLineEdit()
        self.holdings_input.setPlaceholderText("Holdings (e.g., 1.5)")

        self.add_button = QPushButton("Add Coin")
        self.add_button.clicked.connect(self.add_coin)

        self.help_button = QPushButton("View Supported Coins")
        self.help_button.clicked.connect(self.show_supported_coins)

        layout.addWidget(QLabel("Enter Coin Details"))
        layout.addWidget(self.coin_name_input)
        layout.addWidget(self.symbol_input)
        layout.addWidget(self.holdings_input)
        layout.addWidget(self.add_button)
        layout.addWidget(self.help_button)

        self.setLayout(layout)

    def add_coin(self):
        coin = self.coin_name_input.text().strip()
        symbol = self.symbol_input.text().strip().upper()
        holdings_text = self.holdings_input.text().strip()

        if not all([coin, symbol, holdings_text]):
            QMessageBox.warning(self, "Input Error", "All fields are required.")
            return

        try:
            holdings = float(holdings_text)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Holdings must be a number.")
            return

        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO user_wallets (username, coin_name, symbol, holdings)
                VALUES (?, ?, ?, ?)
            """, (self.username, coin, symbol, holdings))
            conn.commit()
            conn.close()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add coin:\n{e}")

    def show_supported_coins(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Supported Coins")
        dialog.setFixedSize(350, 450)

        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        inner = QWidget()
        inner_layout = QVBoxLayout()

        prices = fetch_prices(list(SYMBOL_TO_ID.keys()))
        if "error" in prices:
            QMessageBox.critical(self, "API Error", prices["error"])
            return

        for symbol in sorted(prices.keys()):
            coin_info = prices[symbol]
            coin_name = SYMBOL_TO_ID[symbol].replace("-", " ").title()
            logo_url = coin_info.get("image", "")

            h_layout = QHBoxLayout()

            if logo_url:
                try:
                    response = requests.get(logo_url, timeout=5)
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)
                    logo_label = QLabel()
                    logo_label.setPixmap(pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    h_layout.addWidget(logo_label)
                except:
                    h_layout.addWidget(QLabel("❓"))

            h_layout.addWidget(QLabel(f"{symbol} - {coin_name}"))
            h_layout.addStretch()
            inner_layout.addLayout(h_layout)

        inner.setLayout(inner_layout)
        scroll.setWidget(inner)
        layout.addWidget(scroll)
        dialog.setLayout(layout)
        dialog.exec_()
