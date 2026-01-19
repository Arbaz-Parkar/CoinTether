# 🪙 CoinTether – Crypto Wallet Tracker

**CoinTether** is a desktop-based cryptocurrency wallet tracker built with **Python** and **PyQt5**.  
It helps users manage their crypto portfolios, track live prices, and view real-time valuations in both **USD** and **INR** using the **CoinGecko API**.  

The system includes secure login modules for both users and admins, allowing role-based control and centralized management of user portfolios.

---

## 🚀 Features

- **User & Admin Login:** Secure authentication system with separate access control.  
- **Real-Time Prices:** Fetches live cryptocurrency data from CoinGecko’s public API.  
- **Portfolio Management:** Add, update, or remove coins with automatic total value calculation.  
- **Currency Conversion:** Displays holdings in both USD and INR.  
- **Interactive Dashboard:** Clean PyQt5-based interface with coin logos and modern layout.  
- **Pie Chart View:** Visual representation of portfolio distribution.  
- **Admin Controls:** Manage users, reset passwords, suspend accounts, and view portfolios (read-only).  
- **Local Database:** Uses SQLite for secure offline data storage.  

---

## 🧱 Tech Stack

| Component | Technology Used |
|------------|-----------------|
| Programming Language | Python 3 |
| GUI Framework | PyQt5 |
| Database | SQLite3 |
| API | CoinGecko Public API |
| Development Tools | Visual Studio Code, PyInstaller |
| Operating System | Windows 10 and above |

---

## ⚙️ Installation & Setup

### Option 1: Run from Source  
1. Clone this repository:  
   ```bash
   git clone https://github.com/<your-username>/CoinTether.git
   ```
2. Navigate to the project folder:  
   ```bash
   cd CoinTether
   ```
3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:  
   ```bash
   python src/welcome_screen.py
   ```

---

### Option 2: Run the Compiled App  
After building with **PyInstaller**, run:  
```
dist/CoinTether/CoinTether.exe
```

The compiled app includes all dependencies and runs without requiring Python.

---

## 📂 Folder Structure

```
CoinTether/
│
├── src/
│   ├── welcome_screen.py         # Entry point (Welcome UI)
│   ├── login.py                  # User login module
│   ├── admin_login.py            # Admin login screen
│   ├── dashboard.py              # User dashboard
│   ├── admin_dashboard.py        # Admin dashboard
│   ├── add_coin.py               # Add coin dialog
│   ├── price_fetcher.py          # Fetches prices via CoinGecko API
│   ├── user_wallet_viewer.py     # Wallet viewer for admin
│   └── utils/                    # Helper functions (if any)
│
├── data/
│   └── users.db                  # SQLite database (bundled)
│
├── dist/
│   └── CoinTether.exe            # Compiled executable
│
├── CoinTether.spec               # PyInstaller spec file
├── requirements.txt
└── CoinTether Documentation.docx
```

---

## 💡 System Requirements

**Hardware:**  
- Processor: Intel i3 or above  
- RAM: 4 GB minimum  
- Storage: 40 GB or more  

**Software:**  
- OS: Windows 10 or above  
- Tools: Visual Studio Code (with Python), Chrome Browser, PyInstaller  
- Languages: Python, SQL

---

## 🧑‍💻 Author

**Developed by:**  
**Arbaz Zameer Parkar**  
B.Sc. Computer Science (T.Y.B.Sc.)  
**D. B. J. College, Chiplun (Autonomous)**  
Affiliated to University of Mumbai  
Academic Year: **2025 – 2026**

---

## 📚 References

- [CoinGecko API](https://www.coingecko.com/en/api)
- [GeeksforGeeks.org](https://www.geeksforgeeks.org)
- [StackOverflow.com](https://stackoverflow.com)
- [Python.org](https://www.python.org)

---

## 📦 License

This project is developed for academic and educational purposes.  
Unauthorized commercial use or redistribution is not permitted.
