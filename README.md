# Women Safety Management System (WSMS)

A web-based emergency telemetry and distress response prototype built for academic **Project-Based Learning (PBL)** in Software Engineering (Sem 5).

---

## 📁 Project Structure

```
d:\B.Tech\Sem 5\SE\PBL\
├── app.py                     # Main Flask application with Auth, CSRF, Contacts & SOS routes
├── requirements.txt           # Python package dependencies
├── test_white_box.py          # Automated unittest test suite (20 white-box test cases)
├── Black_Box_Test_Cases.md    # 10 Functional black-box test cases table
├── Project_Report.md          # Comprehensive PBL Academic Project Report
├── Jira_Product_Backlog.md    # Jira Scrum backlog mapping (SCRUM-5 to SCRUM-47)
├── templates/
│   ├── base.html              # Base layout with Bootstrap 5, navbar & hotline banner
│   ├── login.html             # Secure user login with generic error handling
│   ├── register.html          # User registration with password validation
│   ├── dashboard.html         # User command center, recent alerts & quick stats
│   ├── trusted_contacts.html  # Contacts CRUD (max 5 limit & ownership check)
│   └── sos.html               # SOS trigger with HTML5 Geolocation API & fallback
└── static/
    └── css/
        └── style.css          # Safety purple theme, pulsing SOS button & alert badges
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites & Environment Setup
Ensure Python 3.8+ is installed on your system.

```bash
# Optional: Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python app.py
```
Navigate your browser to: **`http://127.0.0.1:5000`**

### 3. Run the White-Box Test Suite
Execute the 20 automated unit tests using Python's built-in `unittest` runner:
```bash
python -m unittest test_white_box.py -v
```

---

## 🛡️ Key Features & Engineering Highlights

- **Authentication & Security:** PBKDF2:SHA256 password hashing (via Werkzeug), session fixation mitigation, parameterization against SQL injection, and cryptographically random CSRF verification tokens.
- **Trusted Contacts Quota:** Users can add up to 5 emergency contacts. The system enforces strict ownership verification (`user_id == session['user_id']`), rejecting unauthorized deletion attempts with HTTP 403 Forbidden.
- **Resilient Geolocation Telemetry:** Captures live GPS coordinates via the HTML5 Geolocation API (`enableHighAccuracy: true`). If location access is denied or times out, the system automatically degrades to fallback mode (`status = 'DENIED'`), allowing users to submit emergency landmark notes without system crash.
- **PBL Documentation & Agile Backlog:** Full IEEE-style project report mapped to Jira backlog items (`SCRUM-5` to `SCRUM-47`).
