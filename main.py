# main.py

from PyQt5.QtWidgets import QApplication
import sys
from src.welcome_screen import WelcomeScreen

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WelcomeScreen()
    window.show()
    sys.exit(app.exec_())
