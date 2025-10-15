# src/user_wallet_viewer.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QLineEdit,
    QHeaderView, QMessageBox, QAbstractItemView
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
import sqlite3
import os
import sys

from src.price_fetcher import fetch_prices


def get_database_path():
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
    return os.path.join(app_dir, 'users.db')


db_path = get_database_path()


class UserWalletViewer(QDialog):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle(f"{username}'s Wallet (Read-Only)")
        self.setFixedSize(700, 500)
        self.init_ui()
        self.apply_dark_theme()
        self.load_wallet_data()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.header = QLabel(f"{self.username}'s Portfolio")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        self.layout.addWidget(self.header)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search coin or symbol...")
        self.search_bar.textChanged.connect(self.filter_table)
        self.layout.addWidget(self.search_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Logo", "Coin", "Symbol", "Holdings"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.layout.addWidget(self.table)

        self.setLayout(self.layout)

    def load_wallet_data(self):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT coin_name, symbol, holdings FROM user_wallets WHERE username = ?", (self.username,))
            self.wallet_data = cursor.fetchall()
            conn.close()

            symbols = list(set([row[1].upper() for row in self.wallet_data]))
            self.price_data = fetch_prices(symbols)
            self.populate_table()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load wallet data:\n{e}")

    def populate_table(self):
        self.table.setRowCount(0)
        for i, (coin, symbol, holdings) in enumerate(self.wallet_data):
            self.table.insertRow(i)

            # Logo
            logo_item = QTableWidgetItem()
            logo_url = self.price_data.get(symbol.upper(), {}).get("image")
            if logo_url:
                try:
                    from urllib.request import urlopen
                    image_data = urlopen(logo_url).read()
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    pixmap = pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    logo_item.setIcon(QIcon(pixmap))
                except:
                    logo_item.setText("N/A")
            else:
                logo_item.setText("N/A")
            self.table.setItem(i, 0, logo_item)

            self.table.setItem(i, 1, QTableWidgetItem(coin))
            self.table.setItem(i, 2, QTableWidgetItem(symbol))
            self.table.setItem(i, 3, QTableWidgetItem(f"{holdings:.4f}"))

        self.table.resizeRowsToContents()

    def filter_table(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            coin = self.table.item(row, 1).text().lower()
            symbol = self.table.item(row, 2).text().lower()
            match = text in coin or text in symbol
            self.table.setRowHidden(row, not match)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: Segoe UI, sans-serif;
            }
            QTableWidget {
                background-color: #2C2C2C;
                color: white;
                border: 1px solid #444;
            }
            QHeaderView::section {
                background-color: #2C2C2C;
                color: white;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #444;
            }
            QLineEdit {
                background-color: #2C2C2C;
                color: white;
                padding: 6px;
                border: 1px solid #555;
            }
        """)
