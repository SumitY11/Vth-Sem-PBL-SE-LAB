"""
Women Safety Management System (WSMS)
PBL Project Implementation - Flask Backend & SQLite Database
"""

import os
import re
import sqlite3
import secrets
from datetime import datetime
from functools import wraps
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, jsonify, abort, g
)
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------
# Application Configuration
# ---------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['DATABASE'] = os.environ.get('DATABASE', os.path.join(os.path.dirname(__file__), 'wsms.db'))
app.config['MAX_CONTACTS_PER_USER'] = 5

# ---------------------------------------------------------
# Database Utilities
# ---------------------------------------------------------
def get_db():
    """Opens a new database connection if there is none yet for the current app context."""
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
        # Enable foreign key enforcement in SQLite
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    """Closes the database at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database schema."""
    db = get_db()
    cursor = db.cursor()
    
    # 1. Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT NOT NULL,
        password_hash TEXT NOT NULL,
        emergency_message TEXT DEFAULT 'Emergency! I need immediate help. Please track my location.',
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Trusted Contacts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS trusted_contacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        contact_name TEXT NOT NULL,
        contact_phone TEXT NOT NULL,
        relationship TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # 3. SOS Alerts Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sos_alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        latitude REAL,
        longitude REAL,
        accuracy REAL,
        location_status TEXT NOT NULL,
        emergency_notes TEXT,
        status TEXT DEFAULT 'ACTIVE',
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)
    db.commit()

# Ensure database tables exist upon start
with app.app_context():
    init_db()

# ---------------------------------------------------------
# CSRF Protection Utilities
# ---------------------------------------------------------
def generate_csrf_token():
    """Generates and persists a CSRF token in the user session."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

app.jinja_env.globals['csrf_token'] = generate_csrf_token

def verify_csrf(f):
    """Decorator to verify CSRF token on POST requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == "POST":
            # Token can come from form data or HTTP header (for AJAX / fetch requests)
            token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
            expected_token = session.get('_csrf_token')

            if not expected_token or not token or not secrets.compare_digest(token, expected_token):
                if request.is_json or request.headers.get('Accept') == 'application/json':
                    return jsonify({'success': False, 'message': 'CSRF token missing or invalid.'}), 400
                flash('Security verification failed (Invalid or missing CSRF token). Please try again.', 'danger')
                return redirect(request.referrer or url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------
# Authentication & Access Control Decorator
# ---------------------------------------------------------
def login_required(f):
    """Decorator ensuring that the user is authenticated."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this feature.', 'warning')
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------
# Context Processors & Helpers
# ---------------------------------------------------------
@app.context_processor
def inject_user():
    """Injects authenticated user state into all Jinja templates."""
    return {
        'current_user': {
            'id': session.get('user_id'),
            'name': session.get('user_name'),
            'email': session.get('user_email')
        } if 'user_id' in session else None
    }

def is_valid_email(email):
    """Basic regex validation for email."""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None

# ---------------------------------------------------------
# Core Routes
# ---------------------------------------------------------
@app.route('/')
def index():
    """Home landing page or redirect to dashboard if authenticated."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
@verify_csrf
def register():
    """Handles new user registration with strict validation and password hashing."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Input Validation
        if not name or not email or not phone or not password or not confirm_password:
            flash('All registration fields are required.', 'danger')
            return render_template('register.html', name=name, email=email, phone=phone), 400

        if not is_valid_email(email):
            flash('Please provide a valid email address.', 'danger')
            return render_template('register.html', name=name, email=email, phone=phone), 400

        if len(password) < 8:
            flash('Password must be at least 8 characters in length.', 'danger')
            return render_template('register.html', name=name, email=email, phone=phone), 400

        if password != confirm_password:
            flash('Password confirmation does not match.', 'danger')
            return render_template('register.html', name=name, email=email, phone=phone), 400

        db = get_db()
        cursor = db.cursor()

        # Duplicate email check
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            flash('An account with this email address already exists.', 'warning')
            return render_template('register.html', name=name, phone=phone), 400

        # Secure password hashing (Werkzeug scrypt / pbkdf2)
        password_hash = generate_password_hash(password, method='pbkdf2:sha256')

        cursor.execute("""
            INSERT INTO users (name, email, phone, password_hash)
            VALUES (?, ?, ?, ?)
        """, (name, email, phone, password_hash))
        db.commit()

        flash('Registration successful! Please log in to your account.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
@verify_csrf
def login():
    """Handles user login with generic error messages against credential harvesting."""
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'danger')
            return render_template('login.html', email=email), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, name, email, password_hash FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        # Generic response prevents account enumeration attacks
        if not user or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password. Please verify your credentials.', 'danger')
            return render_template('login.html', email=email), 401

        # Secure Session Initialization
        session.clear()
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        session['user_email'] = user['email']
        generate_csrf_token()  # regenerate token for session

        flash(f'Welcome back, {user["name"]}!', 'success')
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    """Clears user session and logs out."""
    session.clear()
    flash('You have been securely logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Renders user dashboard with summary cards, contact counts, and recent SOS history."""
    db = get_db()
    cursor = db.cursor()

    # Fetch trusted contacts count
    cursor.execute("SELECT COUNT(*) as count FROM trusted_contacts WHERE user_id = ?", (session['user_id'],))
    contact_count = cursor.fetchone()['count']

    # Fetch recent SOS alerts
    cursor.execute("""
        SELECT id, timestamp, latitude, longitude, accuracy, location_status, emergency_notes, status
        FROM sos_alerts
        WHERE user_id = ?
        ORDER BY timestamp DESC
        LIMIT 5
    """, (session['user_id'],))
    recent_alerts = cursor.fetchall()

    # Fetch quick contact list
    cursor.execute("""
        SELECT contact_name, contact_phone, relationship
        FROM trusted_contacts
        WHERE user_id = ?
        ORDER BY created_at ASC
    """, (session['user_id'],))
    contacts = cursor.fetchall()

    return render_template(
        'dashboard.html',
        contact_count=contact_count,
        max_contacts=app.config['MAX_CONTACTS_PER_USER'],
        recent_alerts=recent_alerts,
        contacts=contacts
    )

# ---------------------------------------------------------
# Trusted Contacts Management (CRUD)
# ---------------------------------------------------------
@app.route('/trusted-contacts')
@login_required
def trusted_contacts():
    """Displays user's trusted contacts with addition form."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""
        SELECT id, contact_name, contact_phone, relationship, created_at
        FROM trusted_contacts
        WHERE user_id = ?
        ORDER BY created_at ASC
    """, (session['user_id'],))
    contacts = cursor.fetchall()

    return render_template(
        'trusted_contacts.html',
        contacts=contacts,
        current_count=len(contacts),
        max_contacts=app.config['MAX_CONTACTS_PER_USER']
    )

@app.route('/trusted-contacts/add', methods=['POST'])
@login_required
@verify_csrf
def add_trusted_contact():
    """Adds a new trusted contact, enforcing a maximum limit of 5 contacts per user."""
    name = request.form.get('contact_name', '').strip()
    phone = request.form.get('contact_phone', '').strip()
    relationship = request.form.get('relationship', '').strip()

    if not name or not phone or not relationship:
        flash('All contact fields (name, phone, relationship) are required.', 'danger')
        return redirect(url_for('trusted_contacts'))

    db = get_db()
    cursor = db.cursor()

    # Check maximum contact limit
    cursor.execute("SELECT COUNT(*) as count FROM trusted_contacts WHERE user_id = ?", (session['user_id'],))
    count = cursor.fetchone()['count']

    if count >= app.config['MAX_CONTACTS_PER_USER']:
        flash(f'Maximum limit reached. You can only maintain up to {app.config["MAX_CONTACTS_PER_USER"]} trusted contacts.', 'warning')
        return redirect(url_for('trusted_contacts'))

    cursor.execute("""
        INSERT INTO trusted_contacts (user_id, contact_name, contact_phone, relationship)
        VALUES (?, ?, ?, ?)
    """, (session['user_id'], name, phone, relationship))
    db.commit()

    flash(f'Trusted contact "{name}" successfully added.', 'success')
    return redirect(url_for('trusted_contacts'))

@app.route('/trusted-contacts/delete/<int:contact_id>', methods=['POST'])
@login_required
@verify_csrf
def delete_trusted_contact(contact_id):
    """Deletes a trusted contact with strict ownership check."""
    db = get_db()
    cursor = db.cursor()

    # Verify contact existence and ownership
    cursor.execute("SELECT id, user_id, contact_name FROM trusted_contacts WHERE id = ?", (contact_id,))
    contact = cursor.fetchone()

    if not contact:
        flash('Contact record not found.', 'danger')
        return redirect(url_for('trusted_contacts'))

    # Strict authorization check
    if contact['user_id'] != session['user_id']:
        abort(403)  # Forbidden: User does not own this resource

    cursor.execute("DELETE FROM trusted_contacts WHERE id = ?", (contact_id,))
    db.commit()

    flash(f'Trusted contact "{contact["contact_name"]}" was deleted.', 'info')
    return redirect(url_for('trusted_contacts'))

# ---------------------------------------------------------
# Emergency SOS Alert Management & Geolocation Fallback
# ---------------------------------------------------------
@app.route('/sos', methods=['GET', 'POST'])
@login_required
@verify_csrf
def sos():
    """
    Renders the SOS trigger page (GET) and processes emergency alert dispatches (POST).
    Captures GPS coordinates or executes fallback parsing when geolocation is denied/unavailable.
    """
    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Accept either JSON payload or Form data
        if request.is_json:
            data = request.get_json() or {}
            raw_lat = data.get('latitude')
            raw_lng = data.get('longitude')
            raw_acc = data.get('accuracy')
            location_status = data.get('location_status', 'UNKNOWN').strip()
            emergency_notes = data.get('emergency_notes', '').strip()
        else:
            raw_lat = request.form.get('latitude')
            raw_lng = request.form.get('longitude')
            raw_acc = request.form.get('accuracy')
            location_status = request.form.get('location_status', 'UNKNOWN').strip()
            emergency_notes = request.form.get('emergency_notes', '').strip()

        # Parse & Validate Coordinates or Fallback
        latitude = None
        longitude = None
        accuracy = None

        if location_status == 'ACQUIRED' and raw_lat is not None and raw_lng is not None:
            try:
                latitude = float(raw_lat)
                longitude = float(raw_lng)
                if raw_acc is not None:
                    accuracy = float(raw_acc)
            except (ValueError, TypeError):
                location_status = 'INVALID_COORDINATES'
                latitude = None
                longitude = None
        else:
            # Fallback protocol if location is DENIED, UNAVAILABLE, or TIMEOUT
            if location_status not in ['DENIED', 'UNAVAILABLE', 'TIMEOUT', 'MANUAL_FALLBACK']:
                location_status = 'DENIED'

        # Record SOS Alert in Database
        cursor.execute("""
            INSERT INTO sos_alerts (user_id, latitude, longitude, accuracy, location_status, emergency_notes, status)
            VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
        """, (session['user_id'], latitude, longitude, accuracy, location_status, emergency_notes))
        alert_id = cursor.lastrowid
        db.commit()

        # Retrieve user's trusted contacts for simulated alert dispatch
        cursor.execute("""
            SELECT contact_name, contact_phone, relationship
            FROM trusted_contacts
            WHERE user_id = ?
        """, (session['user_id'],))
        contacts = cursor.fetchall()

        contact_list = [
            {'name': c['contact_name'], 'phone': c['contact_phone'], 'relationship': c['relationship']}
            for c in contacts
        ]

        response_payload = {
            'success': True,
            'alert_id': alert_id,
            'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC'),
            'location_status': location_status,
            'latitude': latitude,
            'longitude': longitude,
            'accuracy': accuracy,
            'notified_contacts': contact_list,
            'message': 'EMERGENCY SOS BROADCAST ACTIVATED! Notification dispatched to all registered contacts.'
        }

        if request.is_json or request.headers.get('Accept') == 'application/json':
            return jsonify(response_payload), 200

        flash('EMERGENCY SOS ACTIVATED: Your alert has been logged and broadcast dispatched!', 'danger')
        return redirect(url_for('dashboard'))

    # GET Request: Fetch user's registered contacts to display on the SOS trigger page
    cursor.execute("""
        SELECT contact_name, contact_phone, relationship
        FROM trusted_contacts
        WHERE user_id = ?
    """, (session['user_id'],))
    contacts = cursor.fetchall()

    cursor.execute("SELECT emergency_message FROM users WHERE id = ?", (session['user_id'],))
    user_row = cursor.fetchone()
    custom_msg = user_row['emergency_message'] if user_row else ''

    return render_template('sos.html', contacts=contacts, custom_message=custom_msg)

# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

