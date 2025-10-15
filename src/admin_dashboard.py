# src/admin_dashboard.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox,
    QTableWidget, QTableWidgetItem, QDialog, QTextEdit, QInputDialog,
    QLineEdit, QHeaderView, QAbstractItemView, QFileDialog
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt
import os, sqlite3, hashlib, csv, datetime
from fpdf import FPDF

from src.user_wallet_viewer import UserWalletViewer

def get_database_path():
    import sys
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    return os.path.join(app_dir, 'data', 'users.db')

db_path = get_database_path()

class AdminDashboard(QWidget):
    def __init__(self, admin_username):
        super().__init__()
        self.admin_username = admin_username
        self.setWindowTitle("CoinTether - Admin Dashboard")
        self.setFixedSize(900, 700)
        self.notifications = []
        self.setup_ui()
        self.apply_dark_theme()
        self.load_users()

    def setup_ui(self):
        layout = QVBoxLayout()

        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'assets', 'CoinTether_Logo.png'))
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path).scaledToHeight(60, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

        title = QLabel(f"Welcome Admin: {self.admin_username}")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search users by username or email...")
        self.search_bar.textChanged.connect(self.filter_table)
        layout.addWidget(self.search_bar)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Username", "Email", "Total USD+INR", "Coins", "Status", "Actions"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        layout.addWidget(self.table)

        btn_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.load_users)

        self.batch_suspend_btn = QPushButton("Suspend Selected")
        self.batch_suspend_btn.clicked.connect(self.batch_suspend)

        self.batch_unban_btn = QPushButton("Unban Selected")
        self.batch_unban_btn.clicked.connect(self.batch_unban)

        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.clicked.connect(self.export_csv)

        self.export_pdf_btn = QPushButton("Export PDF")
        self.export_pdf_btn.clicked.connect(self.export_pdf)

        self.notifications_btn = QPushButton("Notifications")
        self.notifications_btn.clicked.connect(self.show_notifications)

        self.logout_btn = QPushButton("Logout")
        self.logout_btn.clicked.connect(self.logout)

        self.settings_btn = QPushButton("⚙️ Settings")
        self.settings_btn.clicked.connect(self.open_settings)

        for b in [self.refresh_btn, self.batch_suspend_btn, self.batch_unban_btn,
                  self.export_csv_btn, self.export_pdf_btn, self.notifications_btn,
                  self.settings_btn, self.logout_btn]:
            btn_layout.addWidget(b)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

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
            QLineEdit, QTableWidget {
                background-color: #2C2C2C;
                color: white;
                border: 1px solid #444;
                padding: 4px;
                border-radius: 4px;
            }
            QPushButton {
                font-size: 14px;
                background-color: #27AE60;
                color: white;
                padding: 6px;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #2ECC71; }
            QHeaderView::section {
                background-color: #2C2C2C;
                color: white;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #444;
            }
        """)

    def load_users(self):
        self.table.setRowCount(0)
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS user_flags (username TEXT PRIMARY KEY, suspended INTEGER DEFAULT 0);""")
            cur.execute("""CREATE TABLE IF NOT EXISTS user_notes (username TEXT, note TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);""")
            conn.commit()

            cur.execute("SELECT username, email FROM users")
            users = cur.fetchall()

            for row_idx, (username, email) in enumerate(users):
                cur.execute("SELECT SUM(holdings) FROM user_wallets WHERE username=?", (username,))
                total = cur.fetchone()[0] or 0

                coin_count = cur.execute("SELECT COUNT(*) FROM user_wallets WHERE username=?", (username,)).fetchone()[0]

                flag = cur.execute("SELECT suspended FROM user_flags WHERE username=?", (username,)).fetchone()
                suspended = "Suspended" if flag and flag[0] else "Active"

                self.table.insertRow(row_idx)
                self.table.setItem(row_idx, 0, QTableWidgetItem(username))
                self.table.setItem(row_idx, 1, QTableWidgetItem(email))
                self.table.setItem(row_idx, 2, QTableWidgetItem(f"{total:.2f}"))
                self.table.setItem(row_idx, 3, QTableWidgetItem(str(coin_count)))
                self.table.setItem(row_idx, 4, QTableWidgetItem(suspended))

                btn_widget = QWidget()
                btn_layout = QHBoxLayout()
                btn_layout.setContentsMargins(0,0,0,0)
                btn_layout.setSpacing(4)

                def make_btn(text, tip, func):
                    b = QPushButton(text)
                    b.setToolTip(tip)
                    b.setFixedSize(32, 32)
                    b.clicked.connect(lambda _, u=username: func(u))
                    return b

                view_btn = make_btn("👁", "View Wallet", self.view_wallet)
                reset_btn = make_btn("🔁", "Reset Password", self.reset_password)
                ban_btn = make_btn("🚫" if suspended=="Active" else "🔓", "Ban/Unban", self.toggle_suspend)
                delete_btn = make_btn("🗑", "Delete User", self.delete_user)
                note_btn = make_btn("📝", "Send Note", self.send_note)

                for b in [view_btn, reset_btn, ban_btn, delete_btn, note_btn]:
                    btn_layout.addWidget(b)

                btn_widget.setLayout(btn_layout)
                self.table.setCellWidget(row_idx, 5, btn_widget)

            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def filter_table(self, text):
        text = text.lower()
        for row in range(self.table.rowCount()):
            username = self.table.item(row,0).text().lower()
            email = self.table.item(row,1).text().lower()
            matches = text in username or text in email
            self.table.setRowHidden(row, not matches)

    # ---------------------- User Actions ----------------------
    def view_wallet(self, username):
        dialog = UserWalletViewer(username)
        dialog.exec_()

    def reset_password(self, username):
        new_pwd, ok = QInputDialog.getText(self, "Reset Password", f"Enter new password for {username}:")
        if ok and new_pwd:
            hashed = hashlib.sha256(new_pwd.encode()).hexdigest()
            try:
                conn = sqlite3.connect(db_path)
                conn.execute("UPDATE users SET password=? WHERE username=?", (hashed, username))
                conn.commit()
                conn.close()
                self.add_notification(f"Password reset for {username}.")
                QMessageBox.information(self, "Success", f"Password reset for {username}.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def toggle_suspend(self, username):
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT suspended FROM user_flags WHERE username=?", (username,))
            flag = cur.fetchone()
            if flag:
                new_status = 0 if flag[0] else 1
                cur.execute("UPDATE user_flags SET suspended=? WHERE username=?", (new_status, username))
            else:
                cur.execute("INSERT INTO user_flags (username, suspended) VALUES (?, 1)", (username,))
            conn.commit()
            conn.close()
            self.load_users()
            self.add_notification(f"Toggled suspension for {username}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def delete_user(self, username):
        confirm = QMessageBox.question(self, "Confirm", f"Delete account and data for {username}?", QMessageBox.Yes | QMessageBox.No)
        if confirm != QMessageBox.Yes: return
        try:
            conn = sqlite3.connect(db_path)
            for table in ["users","user_wallets","user_flags","user_notes"]:
                conn.execute(f"DELETE FROM {table} WHERE username=?", (username,))
            conn.commit()
            conn.close()
            self.load_users()
            self.add_notification(f"Deleted user {username}.")
            QMessageBox.information(self, "Deleted", f"{username}'s account deleted.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def send_note(self, username):
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Send Note to {username}")
        layout = QVBoxLayout()
        note_input = QTextEdit()
        layout.addWidget(note_input)
        send_btn = QPushButton("Send")
        send_btn.clicked.connect(lambda: self._save_note(dialog, username, note_input.toPlainText()))
        layout.addWidget(send_btn)
        dialog.setLayout(layout)
        dialog.exec_()

    def _save_note(self, dialog, username, note):
        if not note.strip():
            QMessageBox.warning(dialog, "Empty", "Note cannot be empty.")
            return
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("INSERT INTO user_notes (username, note) VALUES (?, ?)", (username, note.strip()))
            conn.commit()
            conn.close()
            self.add_notification(f"Sent note to {username}.")
            dialog.accept()
        except Exception as e:
            QMessageBox.critical(dialog, "Error", str(e))

    # ---------------------- Batch Actions ----------------------
    def batch_suspend(self):
        selected = self.table.selectedItems()
        usernames = list({self.table.item(i.row(),0).text() for i in selected})
        for user in usernames: self.toggle_suspend(user)

    def batch_unban(self):
        selected = self.table.selectedItems()
        usernames = list({self.table.item(i.row(),0).text() for i in selected})
        for user in usernames:
            try:
                conn = sqlite3.connect(db_path)
                cur = conn.cursor()
                cur.execute("UPDATE user_flags SET suspended=0 WHERE username=?", (user,))
                conn.commit(); conn.close()
                self.load_users()
                self.add_notification(f"Unbanned {user}.")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    # ---------------------- Export ----------------------
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if not path: return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Username","Email","Total USD+INR","Coins","Status"])
                for row in range(self.table.rowCount()):
                    writer.writerow([self.table.item(row,i).text() for i in range(5)])
            QMessageBox.information(self, "CSV Exported", f"CSV saved to {path}")
            self.add_notification(f"Exported CSV to {path}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def export_pdf(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if not path: return
        try:
            pdf = FPDF(); pdf.add_page(); pdf.set_font("Arial","B",16)
            pdf.cell(0,10,"CoinTether Admin User Report", ln=True, align="C"); pdf.ln(10)
            pdf.set_font("Arial","",12)
            for row in range(self.table.rowCount()):
                pdf.cell(0,8," | ".join([self.table.item(row,i).text() for i in range(5)]), ln=True)
            pdf.output(path)
            QMessageBox.information(self, "PDF Exported", f"PDF saved to {path}")
            self.add_notification(f"Exported PDF to {path}.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    # ---------------------- Notifications ----------------------
    def add_notification(self, text):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.notifications.append(f"[{timestamp}] {text}")

    def show_notifications(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Admin Notifications")
        layout = QVBoxLayout()
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setText("\n".join(self.notifications[-50:]))  # last 50 actions
        layout.addWidget(text_area)
        dialog.setLayout(layout)
        dialog.exec_()

    # ---------------------- Admin Settings ----------------------
    def open_settings(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Admin Settings - Change Password")
        layout = QVBoxLayout()
        current_label, current_input = QLabel("Current Password:"), QLineEdit()
        current_input.setEchoMode(QLineEdit.Password)
        new_label, new_input = QLabel("New Password:"), QLineEdit(); new_input.setEchoMode(QLineEdit.Password)
        confirm_label, confirm_input = QLabel("Confirm New Password:"), QLineEdit(); confirm_input.setEchoMode(QLineEdit.Password)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_admin_password(dialog, current_input.text(), new_input.text(), confirm_input.text()))
        for w in [current_label,current_input,new_label,new_input,confirm_label,confirm_input,save_btn]:
            layout.addWidget(w)
        dialog.setLayout(layout)
        dialog.exec_()

    def save_admin_password(self, dialog, current_pwd, new_pwd, confirm_pwd):
        if not current_pwd or not new_pwd or not confirm_pwd:
            QMessageBox.warning(dialog,"Input Error","All fields are required."); return
        if new_pwd != confirm_pwd:
            QMessageBox.warning(dialog,"Mismatch","New passwords do not match."); return
        try:
            conn = sqlite3.connect(db_path); cur = conn.cursor()
            cur.execute("SELECT password FROM admins WHERE username=?",(self.admin_username,))
            result = cur.fetchone()
            if not result: QMessageBox.critical(dialog,"Error","Admin not found."); conn.close(); return
            if hashlib.sha256(current_pwd.encode()).hexdigest()!=result[0]:
                QMessageBox.warning(dialog,"Error","Current password is incorrect."); conn.close(); return
            cur.execute("UPDATE admins SET password=? WHERE username=?", (hashlib.sha256(new_pwd.encode()).hexdigest(), self.admin_username))
            conn.commit(); conn.close()
            QMessageBox.information(dialog,"Success","Password updated successfully."); dialog.accept()
            self.add_notification("Admin changed their password.")
        except Exception as e:
            QMessageBox.critical(dialog,"Error",str(e))

    # ---------------------- Logout ----------------------
    def logout(self):
        from src.login import UserLoginScreen
        self.login_screen = UserLoginScreen()
        self.login_screen.show()
        self.close()
