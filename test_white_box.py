"""
White-Box Testing Suite for Women Safety Management System (WSMS)
Utilizes Python's unittest and Flask test client.
"""

import os
import unittest
import tempfile
import sqlite3
import json
from werkzeug.security import check_password_hash
from app import app, init_db, get_db

class WSMSWhiteBoxTestCase(unittest.TestCase):
    """Unit and White-Box Test Cases covering internal code paths, validation, CSRF, and data integrity."""

    def setUp(self):
        """Configure test client, temporary database, and testing flags."""
        self.db_fd, self.db_path = tempfile.mkstemp()
        app.config['DATABASE'] = self.db_path
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = True  # Ensure CSRF validation is active
        self.client = app.test_client()

        with app.app_context():
            init_db()

    def tearDown(self):
        """Clean up and close temporary test database."""
        os.close(self.db_fd)
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    # -------------------------------------------------------------
    # Helper Utilities
    # -------------------------------------------------------------
    def get_csrf_token(self):
        """Extracts valid CSRF token by establishing a session via GET request."""
        with self.client.session_transaction() as sess:
            from app import generate_csrf_token
            return generate_csrf_token()

    def register_user(self, name="Jane Doe", email="jane@example.com", phone="+1234567890",
                      password="Password123", confirm_password="Password123", csrf=True):
        """Helper to register a user via test client."""
        token = self.get_csrf_token() if csrf else ""
        return self.client.post('/register', data={
            'name': name,
            'email': email,
            'phone': phone,
            'password': password,
            'confirm_password': confirm_password,
            'csrf_token': token
        }, follow_redirects=True)

    def login_user(self, email="jane@example.com", password="Password123", csrf=True):
        """Helper to log in a user."""
        token = self.get_csrf_token() if csrf else ""
        return self.client.post('/login', data={
            'email': email,
            'password': password,
            'csrf_token': token
        }, follow_redirects=True)

    # -------------------------------------------------------------
    # 1. Registration Input Validation Tests
    # -------------------------------------------------------------
    def test_registration_success(self):
        """TC-WB-01: Successful registration creates user record with hashed password."""
        response = self.register_user(email="alice@example.com")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration successful!", response.data)

        # Verify password is not plain text in SQLite
        with app.app_context():
            db = get_db()
            user = db.execute("SELECT * FROM users WHERE email = ?", ("alice@example.com",)).fetchone()
            self.assertIsNotNone(user)
            self.assertNotEqual(user['password_hash'], "Password123")
            self.assertTrue(check_password_hash(user['password_hash'], "Password123"))

    def test_registration_rejects_empty_fields(self):
        """TC-WB-02: Registration fails when required fields are missing or empty."""
        token = self.get_csrf_token()
        response = self.client.post('/register', data={
            'name': '',
            'email': 'incomplete@example.com',
            'phone': '123456',
            'password': 'Password123',
            'confirm_password': 'Password123',
            'csrf_token': token
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"All registration fields are required", response.data)

    def test_registration_rejects_short_password(self):
        """TC-WB-03: Registration rejects passwords under 8 characters."""
        response = self.register_user(password="short1", confirm_password="short1")
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Password must be at least 8 characters", response.data)

    def test_registration_rejects_mismatched_password(self):
        """TC-WB-04: Registration rejects confirmation mismatch."""
        response = self.register_user(password="Password123", confirm_password="Password999")
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Password confirmation does not match", response.data)

    def test_registration_rejects_invalid_email(self):
        """TC-WB-05: Registration rejects malformed email addresses."""
        response = self.register_user(email="not-a-valid-email")
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"Please provide a valid email address", response.data)

    def test_registration_duplicate_email(self):
        """TC-WB-06: Registration rejects duplicate email addresses."""
        self.register_user(email="duplicate@example.com")
        response = self.register_user(email="duplicate@example.com")
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"already exists", response.data)

    # -------------------------------------------------------------
    # 2. CSRF Protection Tests
    # -------------------------------------------------------------
    def test_missing_csrf_token_rejected_in_post(self):
        """TC-WB-07: POST request with missing CSRF token is rejected."""
        # Make a POST request without any csrf_token parameter
        response = self.client.post('/register', data={
            'name': 'CSRF Attacker',
            'email': 'attacker@example.com',
            'phone': '000000',
            'password': 'Password123',
            'confirm_password': 'Password123'
        }, follow_redirects=True)
        self.assertIn(b"Security verification failed", response.data)

    def test_invalid_csrf_token_rejected_in_post(self):
        """TC-WB-08: POST request with fake CSRF token is rejected."""
        response = self.client.post('/register', data={
            'name': 'CSRF Attacker',
            'email': 'attacker@example.com',
            'phone': '000000',
            'password': 'Password123',
            'confirm_password': 'Password123',
            'csrf_token': 'fake_malicious_token_123456789'
        }, follow_redirects=True)
        self.assertIn(b"Security verification failed", response.data)

    def test_json_post_missing_csrf_returns_400(self):
        """TC-WB-09: JSON API POST request without X-CSRFToken header returns 400 Bad Request."""
        # Log in first
        self.register_user(email="user@test.com")
        self.login_user(email="user@test.com")

        # Make an SOS JSON call without CSRF header
        response = self.client.post('/sos',
            data=json.dumps({'latitude': 12.34, 'longitude': 56.78, 'location_status': 'ACQUIRED'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn("CSRF token missing or invalid", data['message'])

    # -------------------------------------------------------------
    # 3. Authentication & Invalid Login Handling Tests
    # -------------------------------------------------------------
    def test_login_success(self):
        """TC-WB-10: Login with correct credentials establishes session."""
        self.register_user(email="login_user@example.com", password="SecurePassword123")
        response = self.login_user(email="login_user@example.com", password="SecurePassword123")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome back", response.data)

        # Check session state
        with self.client.session_transaction() as sess:
            self.assertIn('user_id', sess)
            self.assertEqual(sess['user_email'], 'login_user@example.com')

    def test_login_invalid_password_generic_error(self):
        """TC-WB-11: Login with wrong password yields generic error response."""
        self.register_user(email="valid_user@example.com", password="RealPassword123")
        token = self.get_csrf_token()
        response = self.client.post('/login', data={
            'email': 'valid_user@example.com',
            'password': 'WrongPassword!',
            'csrf_token': token
        })
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Invalid email or password", response.data)

    def test_login_nonexistent_email_generic_error(self):
        """TC-WB-12: Login with nonexistent email yields identical generic error message."""
        token = self.get_csrf_token()
        response = self.client.post('/login', data={
            'email': 'ghost@example.com',
            'password': 'AnyPassword123',
            'csrf_token': token
        })
        self.assertEqual(response.status_code, 401)
        # Prevents account enumeration
        self.assertIn(b"Invalid email or password", response.data)

    # -------------------------------------------------------------
    # 4. Protected Route Session Redirects
    # -------------------------------------------------------------
    def test_unauthorized_dashboard_redirects_to_login(self):
        """TC-WB-13: Accessing /dashboard while unauthenticated redirects to /login."""
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    def test_unauthorized_trusted_contacts_redirects_to_login(self):
        """TC-WB-14: Accessing /trusted-contacts while unauthenticated redirects to /login."""
        response = self.client.get('/trusted-contacts')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    def test_unauthorized_sos_redirects_to_login(self):
        """TC-WB-15: Accessing /sos while unauthenticated redirects to /login."""
        response = self.client.get('/sos')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.headers['Location'])

    # -------------------------------------------------------------
    # 5. Trusted Contacts CRUD, Limit & Ownership Checks
    # -------------------------------------------------------------
    def test_add_trusted_contact_within_limit(self):
        """TC-WB-16: User can add trusted contacts up to 5."""
        self.register_user(email="contact_tester@example.com")
        self.login_user(email="contact_tester@example.com")
        token = self.get_csrf_token()

        for i in range(1, 6):
            res = self.client.post('/trusted-contacts/add', data={
                'contact_name': f'Contact {i}',
                'contact_phone': f'+100000000{i}',
                'relationship': 'Family',
                'csrf_token': token
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(f"Contact {i}".encode(), res.data)

        # Verify 5 contacts stored in database
        with app.app_context():
            db = get_db()
            count = db.execute("SELECT COUNT(*) as c FROM trusted_contacts").fetchone()['c']
            self.assertEqual(count, 5)

    def test_add_trusted_contact_exceeding_limit_rejected(self):
        """TC-WB-17: Adding 6th contact is blocked with limit error."""
        self.register_user(email="limit_tester@example.com")
        self.login_user(email="limit_tester@example.com")
        token = self.get_csrf_token()

        # Add 5 contacts
        for i in range(1, 6):
            self.client.post('/trusted-contacts/add', data={
                'contact_name': f'Contact {i}',
                'contact_phone': f'+100000000{i}',
                'relationship': 'Friend',
                'csrf_token': token
            })

        # Attempt to add 6th contact
        response = self.client.post('/trusted-contacts/add', data={
            'contact_name': 'Contact 6 (Overflow)',
            'contact_phone': '+1999999999',
            'relationship': 'Neighbor',
            'csrf_token': token
        }, follow_redirects=True)

        self.assertIn(b"Maximum limit reached", response.data)

        with app.app_context():
            db = get_db()
            count = db.execute("SELECT COUNT(*) as c FROM trusted_contacts").fetchone()['c']
            self.assertEqual(count, 5)

    def test_delete_contact_ownership_enforcement(self):
        """TC-WB-18: User cannot delete contacts belonging to another user."""
        # Create User 1 & Add Contact
        self.register_user(email="user1@example.com")
        self.login_user(email="user1@example.com")
        token1 = self.get_csrf_token()
        self.client.post('/trusted-contacts/add', data={
            'contact_name': 'User 1 Emergency Contact',
            'contact_phone': '111-222-3333',
            'relationship': 'Parent',
            'csrf_token': token1
        })

        with app.app_context():
            db = get_db()
            contact = db.execute("SELECT id FROM trusted_contacts WHERE contact_name = 'User 1 Emergency Contact'").fetchone()
            contact_id = contact['id']

        # Log out and log in as User 2
        self.client.get('/logout')
        self.register_user(email="user2@example.com")
        self.login_user(email="user2@example.com")
        token2 = self.get_csrf_token()

        # User 2 attempts to delete User 1's contact
        response = self.client.post(f'/trusted-contacts/delete/{contact_id}', data={
            'csrf_token': token2
        })
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Ensure contact still exists
        with app.app_context():
            db = get_db()
            persisted = db.execute("SELECT id FROM trusted_contacts WHERE id = ?", (contact_id,)).fetchone()
            self.assertIsNotNone(persisted)

    # -------------------------------------------------------------
    # 6. SOS Alert Trigger & Geolocation Fallback Parsing Tests
    # -------------------------------------------------------------
    def test_sos_with_acquired_coordinates(self):
        """TC-WB-19: SOS trigger with valid GPS coordinates is recorded accurately."""
        self.register_user(email="sos_user@example.com")
        self.login_user(email="sos_user@example.com")
        token = self.get_csrf_token()

        payload = {
            'latitude': 28.6139,
            'longitude': 77.2090,
            'accuracy': 12.5,
            'location_status': 'ACQUIRED',
            'emergency_notes': 'Walking home from university station'
        }

        response = self.client.post('/sos',
            data=json.dumps(payload),
            headers={'X-CSRFToken': token, 'Accept': 'application/json'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['location_status'], 'ACQUIRED')
        self.assertEqual(data['latitude'], 28.6139)
        self.assertEqual(data['longitude'], 77.2090)

        # Check database persistence
        with app.app_context():
            db = get_db()
            alert = db.execute("SELECT * FROM sos_alerts WHERE id = ?", (data['alert_id'],)).fetchone()
            self.assertIsNotNone(alert)
            self.assertAlmostEqual(alert['latitude'], 28.6139, places=4)
            self.assertAlmostEqual(alert['longitude'], 77.2090, places=4)
            self.assertEqual(alert['location_status'], 'ACQUIRED')

    def test_sos_with_denied_geolocation_fallback(self):
        """TC-WB-20: SOS trigger with denied location falls back gracefully without crash."""
        self.register_user(email="sos_fallback@example.com")
        self.login_user(email="sos_fallback@example.com")
        token = self.get_csrf_token()

        payload = {
            'latitude': None,
            'longitude': None,
            'accuracy': None,
            'location_status': 'DENIED',
            'emergency_notes': 'Location permission blocked on mobile browser'
        }

        response = self.client.post('/sos',
            data=json.dumps(payload),
            headers={'X-CSRFToken': token, 'Accept': 'application/json'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['location_status'], 'DENIED')
        self.assertIsNone(data['latitude'])
        self.assertIsNone(data['longitude'])

        # Verify fallback recorded in database
        with app.app_context():
            db = get_db()
            alert = db.execute("SELECT * FROM sos_alerts WHERE id = ?", (data['alert_id'],)).fetchone()
            self.assertIsNotNone(alert)
            self.assertEqual(alert['location_status'], 'DENIED')
            self.assertIsNone(alert['latitude'])
            self.assertIsNone(alert['longitude'])

if __name__ == '__main__':
    unittest.main()

