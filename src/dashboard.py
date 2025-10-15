# src/dashboard.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QMessageBox,
    QDialog, QInputDialog, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
import sqlite3, sys, os, requests, smtplib, json, datetime
from email.mime.text import MIMEText
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from fpdf import FPDF

def get_database_path():
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
        return os.path.join(app_dir, 'users.db')
    else:
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        return os.path.join(app_dir, 'users.db')

db_path = get_database_path()
cache_path = os.path.join(os.path.dirname(__file__), 'price_cache.json')
history_path = os.path.join(os.path.dirname(__file__), 'portfolio_history.json')

def send_email(sender_email, sender_password, recipient_email, subject, body):
    try:
        msg = MIMEText(body, "plain")
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True
    except Exception as e:
        return str(e)

def save_price_cache(data):
    try:
        with open(cache_path, 'w') as f:
            json.dump(data, f)
    except: pass

def load_price_cache():
    try:
        with open(cache_path, 'r') as f:
            return json.load(f)
    except: return {}

def save_portfolio_history(username, total_value):
    try:
        history = {}
        if os.path.exists(history_path):
            with open(history_path, 'r') as f:
                history = json.load(f)
        if username not in history:
            history[username] = []
        history[username].append({"timestamp": datetime.datetime.now().isoformat(), "value": total_value})
        with open(history_path, 'w') as f:
            json.dump(history, f)
    except: pass

def load_portfolio_history(username):
    try:
        if os.path.exists(history_path):
            with open(history_path, 'r') as f:
                history = json.load(f)
            return history.get(username, [])
        return []
    except: return []

class UserDashboard(QWidget):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("CoinTether - Dashboard")
        self.setFixedSize(900, 700)
        icon_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'CoinStack.ico'))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.price_cache = load_price_cache()
        self.coin_images = {}
        self.total_usd = 0
        self.total_inr = 0
        self.init_ui()
        self.apply_dark_theme()
        self.ensure_wallet_table()
        self.load_wallet_data()
        self.refresh_prices()

    def init_ui(self):
        layout = QVBoxLayout()
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'CoinTether_Logo.png'))
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaledToHeight(60, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        greeting = QLabel(f"Welcome, {self.username}")
        greeting.setAlignment(Qt.AlignCenter)
        greeting.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(greeting)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by coin name or symbol...")
        self.search_bar.textChanged.connect(self.filter_table)
        layout.addWidget(self.search_bar)
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Logo", "Coin", "Symbol", "Holdings", "USD Price", "INR Price"])
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        self.total_label = QLabel("Total: USD 0.00 | INR 0.00")
        self.total_label.setAlignment(Qt.AlignRight)
        self.total_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 5px;")
        layout.addWidget(self.total_label)
        button_layout = QHBoxLayout()
        self.add_button = QPushButton("Add Coin"); self.add_button.clicked.connect(self.add_coin_dialog)
        self.remove_button = QPushButton("Remove Coin"); self.remove_button.clicked.connect(self.remove_selected_coin)
        self.update_button = QPushButton("Update Holdings"); self.update_button.clicked.connect(self.update_holdings)
        self.refresh_button = QPushButton("Refresh Prices"); self.refresh_button.clicked.connect(self.refresh_prices)
        self.email_button = QPushButton("Email Report"); self.email_button.clicked.connect(self.email_report)
        self.pdf_button = QPushButton("Export PDF"); self.pdf_button.clicked.connect(self.export_pdf)
        self.chart_button = QPushButton("Portfolio Chart"); self.chart_button.clicked.connect(self.show_pie_chart)
        self.history_button = QPushButton("History Graph"); self.history_button.clicked.connect(self.show_history_graph)
        self.logout_button = QPushButton("Logout"); self.logout_button.clicked.connect(self.logout)
        for btn in [self.add_button, self.remove_button, self.update_button, self.refresh_button,
                    self.email_button, self.pdf_button, self.chart_button, self.history_button, self.logout_button]:
            button_layout.addWidget(btn)
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget {background-color: #1E1E1E; color: #FFFFFF; font-family: Segoe UI, sans-serif;}
            QLineEdit, QTableWidget, QTableWidgetItem {background-color: #2C2C2C; border: 1px solid #3A3A3A; color: white; padding: 4px; border-radius: 4px;}
            QHeaderView::section {background-color: #333333; color: white; padding: 4px; border: 1px solid #3A3A3A;}
            QPushButton {background-color: #27AE60; border: none; padding: 6px; color: white; border-radius: 4px;}
            QPushButton:hover {background-color: #2ECC71;}
            QLabel {padding: 2px;}
        """)

    def ensure_wallet_table(self):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_wallets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    coin_name TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    holdings REAL DEFAULT 0
                )
            """)
            conn.commit(); conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"DB Setup Error:\n{e}")

    def load_wallet_data(self):
        self.table.setRowCount(0)
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT coin_name, symbol, holdings FROM user_wallets WHERE username = ?", (self.username,))
            rows = cursor.fetchall(); conn.close()
            for row_idx, (coin, symbol, holdings) in enumerate(rows):
                self.table.insertRow(row_idx)
                self.table.setCellWidget(row_idx, 0, QLabel("Loading..."))
                self.table.setItem(row_idx, 1, QTableWidgetItem(coin))
                self.table.setItem(row_idx, 2, QTableWidgetItem(symbol))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(holdings)))
                self.table.setItem(row_idx, 4, QTableWidgetItem("N/A"))
                self.table.setItem(row_idx, 5, QTableWidgetItem("N/A"))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Load Error:\n{e}")

    def filter_table(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            coin_name = self.table.item(row, 1).text().lower()
            symbol = self.table.item(row, 2).text().lower()
            matches = text in coin_name or text in symbol
            self.table.setRowHidden(row, not matches)

    def refresh_prices(self):
        from src.price_fetcher import fetch_prices
        symbols = [self.table.item(row, 2).text().upper() for row in range(self.table.rowCount())]
        if not symbols: return

        try:
            fetched = fetch_prices(symbols)
            if "error" in fetched:
                QMessageBox.warning(self, "Price Fetch Error", fetched["error"])
                return

            self.price_cache = fetched
            save_price_cache(self.price_cache)

            total_usd, total_inr = 0.0, 0.0
            for row in range(self.table.rowCount()):
                symbol = self.table.item(row, 2).text().upper()
                price_data = self.price_cache.get(symbol, {"usd": "N/A", "inr": "N/A", "image": None})

                self.table.setItem(row, 4, QTableWidgetItem(str(price_data["usd"])))
                self.table.setItem(row, 5, QTableWidgetItem(str(price_data["inr"])))

                if price_data.get("image") and symbol not in self.coin_images:
                    try:
                        response = requests.get(price_data["image"])
                        pixmap = QPixmap()
                        pixmap.loadFromData(response.content)
                        self.coin_images[symbol] = pixmap
                    except: continue

                if symbol in self.coin_images:
                    label = QLabel()
                    label.setPixmap(self.coin_images[symbol].scaled(32, 32))
                    label.setAlignment(Qt.AlignCenter)
                    self.table.setCellWidget(row, 0, label)

                try:
                    holdings = float(self.table.item(row, 3).text())
                    usd = float(self.table.item(row, 4).text())
                    inr = float(self.table.item(row, 5).text())
                    total_usd += holdings * usd
                    total_inr += holdings * inr
                except: continue

            self.total_label.setText(f"Total: USD {total_usd:,.2f} | INR {total_inr:,.2f}")
            self.total_usd, self.total_inr = total_usd, total_inr
            save_portfolio_history(self.username, total_usd + total_inr)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh prices:\n{e}")

    def email_report(self):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT email FROM users WHERE username = ?", (self.username,))
            recipient_email = cursor.fetchone()[0]; conn.close()
        except:
            QMessageBox.critical(self, "Error", "Failed to fetch your registered email."); return
        report = f"CoinTether Portfolio Report for {self.username}:\n\n"
        report += "{:<15} {:<8} {:<12} {:<12}\n".format("Coin", "Symbol", "Holdings", "Value (USD | INR)")
        report += "-"*55 + "\n"
        for row in range(self.table.rowCount()):
            try:
                coin = self.table.item(row, 1).text()
                symbol = self.table.item(row, 2).text()
                holdings = float(self.table.item(row, 3).text())
                usd = float(self.table.item(row, 4).text())
                inr = float(self.table.item(row, 5).text())
                report += "{:<15} {:<8} {:<12,.4f} USD {:<12,.2f} | INR {:<12,.2f}\n".format(coin, symbol, holdings, usd*holdings, inr*holdings)
            except: continue
        confirm = QMessageBox.question(self, "Send Report", f"Send portfolio report to {recipient_email}?", QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes: return
        sender_email = "CoinTetherInc@gmail.com"; sender_password = "mojmrsmigjmpwehf"
        result = send_email(sender_email, sender_password, recipient_email, "CoinTether Portfolio Report", report)
        if result is True: QMessageBox.information(self, "Success", f"Report emailed to {recipient_email}")
        else: QMessageBox.critical(self, "Error", f"Failed to send email:\n{result}")

    def export_pdf(self):
        pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"{self.username} Portfolio Report", ln=True, align="C")
        pdf.set_font("Arial", "", 12); pdf.ln(10)
        pdf.cell(0, 8, "{:<15} {:<8} {:<12} {:<25}".format("Coin", "Symbol", "Holdings", "Value (USD | INR)"), ln=True)
        pdf.cell(0, 8, "-"*65, ln=True)
        for row in range(self.table.rowCount()):
            try:
                coin = self.table.item(row, 1).text()
                symbol = self.table.item(row, 2).text()
                holdings = float(self.table.item(row, 3).text())
                usd = float(self.table.item(row, 4).text())
                inr = float(self.table.item(row, 5).text())
                pdf.cell(0, 8, "{:<15} {:<8} {:<12,.4f} USD {:<12,.2f} | INR {:<12,.2f}".format(
                    coin, symbol, holdings, usd*holdings, inr*holdings
                ), ln=True)
            except: continue
        path = os.path.join(os.path.expanduser("~"), f"{self.username}_portfolio.pdf")
        pdf.output(path)
        QMessageBox.information(self, "PDF Saved", f"Portfolio PDF saved to:\n{path}")

    def add_coin_dialog(self):
        from src.add_coin import AddCoinDialog
        dialog = AddCoinDialog(self.username, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_wallet_data(); self.refresh_prices()

    def remove_selected_coin(self):
        selected = self.table.currentRow()
        if selected == -1: QMessageBox.warning(self, "Select Coin", "Please select a coin to remove."); return
        coin_name = self.table.item(selected, 1).text(); symbol = self.table.item(selected, 2).text()
        confirm = QMessageBox.question(self, "Confirm Delete", f"Are you sure you want to remove {coin_name} ({symbol})?", QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes: return
        try:
            conn = sqlite3.connect(db_path); cursor = conn.cursor()
            cursor.execute("DELETE FROM user_wallets WHERE username = ? AND coin_name = ? AND symbol = ?", (self.username, coin_name, symbol))
            conn.commit(); conn.close()
            self.load_wallet_data(); self.refresh_prices()
        except Exception as e: QMessageBox.critical(self, "Error", f"Failed to delete:\n{e}")

    def update_holdings(self):
        selected = self.table.currentRow()
        if selected == -1: QMessageBox.warning(self, "Select Coin", "Please select a coin to update."); return
        coin_name = self.table.item(selected, 1).text(); symbol = self.table.item(selected, 2).text()
        current_holdings = self.table.item(selected, 3).text()
        new_value, ok = QInputDialog.getDouble(self, "Update Holdings", f"Enter new holdings for {coin_name} ({symbol}):", float(current_holdings), 0, 9999999, 8)
        if ok:
            try:
                conn = sqlite3.connect(db_path); cursor = conn.cursor()
                cursor.execute("UPDATE user_wallets SET holdings = ? WHERE username = ? AND coin_name = ? AND symbol = ?", (new_value, self.username, coin_name, symbol))
                conn.commit(); conn.close()
                self.load_wallet_data(); self.refresh_prices()
            except Exception as e: QMessageBox.critical(self, "Error", f"Failed to update:\n{e}")

    def show_pie_chart(self):
        data = {}
        for row in range(self.table.rowCount()):
            try:
                coin = self.table.item(row, 1).text()
                usd_price = float(self.table.item(row, 4).text()); inr_price = float(self.table.item(row, 5).text())
                holdings = float(self.table.item(row, 3).text())
                data[coin] = {"usd": usd_price * holdings, "inr": inr_price * holdings}
            except: continue
        if not data: QMessageBox.information(self, "No Data", "No holdings to display."); return
        chart_dialog = QDialog(self); chart_dialog.setWindowTitle("Portfolio Distribution"); chart_dialog.setFixedSize(500, 450)
        layout = QVBoxLayout(chart_dialog); fig = Figure(); canvas = FigureCanvas(fig); layout.addWidget(canvas)
        ax = fig.add_subplot(111); labels, values = [], []
        for coin, vals in data.items(): labels.append(f"{coin}\nUSD {vals['usd']:,.2f}\nINR {vals['inr']:,.2f}"); values.append(vals['usd'] + vals['inr'])
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90); ax.set_title("Portfolio Distribution (USD + INR)"); ax.axis('equal'); canvas.draw()
        chart_dialog.exec_()

    def show_history_graph(self):
        history = load_portfolio_history(self.username)
        if not history: QMessageBox.information(self, "No Data", "No portfolio history available."); return
        timestamps = [datetime.datetime.fromisoformat(h["timestamp"]) for h in history]
        values = [h["value"] for h in history]
        dialog = QDialog(self); dialog.setWindowTitle("Portfolio Value History"); dialog.setFixedSize(600, 450)
        layout = QVBoxLayout(dialog); fig = Figure(); canvas = FigureCanvas(fig); layout.addWidget(canvas)
        ax = fig.add_subplot(111); ax.plot(timestamps, values, marker='o', color='#27AE60')
        ax.set_xlabel("Time"); ax.set_ylabel("Total Portfolio Value (USD + INR)")
        ax.set_title("Portfolio Value History"); ax.grid(True); fig.autofmt_xdate()
        canvas.draw(); dialog.exec_()

    def logout(self):
        from src.login import UserLoginScreen
        self.login_screen = UserLoginScreen(); self.login_screen.show(); self.close()
