# Jira Product Backlog & Scrum Task Board Mapping

**Project Name:** Women Safety Management System (WSMS)  
**Project Key:** `SCRUM`  
**Board Type:** Scrum / Kanban Board  
**Target Sprint Cycle:** Sprint 1 to Sprint 4 (Academic Sem 5 PBL)  

---

## 1. Epics Overview (High-Level Work Streams)

| Epic Key | Epic Name | Summary Description | Priority |
| :--- | :--- | :--- | :--- |
| **SCRUM-5** | **EPIC 1: User Authentication & Security** | Core user identity, registration, session management, and credential protection. | Highest |
| **SCRUM-6** | **EPIC 2: Trusted Emergency Contacts** | Emergency circle CRUD operations, 5-contact quota ceiling, and ownership isolation. | High |
| **SCRUM-7** | **EPIC 3: Geolocation Telemetry & Fallbacks** | W3C HTML5 Geolocation sensor integration, accuracy acquisition, and denial fallback. | Highest |
| **SCRUM-8** | **EPIC 4: Emergency SOS Alert Dispatch** | One-tap emergency dispatch button, database persistence, and simulated broadcast. | Highest |
| **SCRUM-9** | **EPIC 5: Dashboard & Incident Audit** | User command center, recent incident history logs, and external mapping links. | Medium |
| **SCRUM-10** | **EPIC 6: Quality Assurance & Documentation** | White-box test suites, functional black-box verification matrix, and PBL project report. | High |

---

## 2. Product Backlog Items (SCRUM-11 to SCRUM-47)

### Category A: Authentication & Identity Management (SCRUM-11 to SCRUM-20)

| Issue Key | Type | Epic Link | Summary | Acceptance Criteria | Story Points | Priority |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **SCRUM-11** | Story | SCRUM-5 | User Registration Form Implementation | Registration page with Name, Email, Phone, Password, and Confirm Password fields. | 3 | High |
| **SCRUM-12** | Task | SCRUM-5 | Registration Input Validation | Form rejects empty inputs and passwords under 8 characters with HTTP 400. | 2 | High |
| **SCRUM-13** | Task | SCRUM-5 | Unique Email Constraint Enforcement | System checks SQLite users table; rejects duplicate emails with clear error alert. | 2 | High |
| **SCRUM-14** | Task | SCRUM-5 | Secure Password Hashing via Werkzeug | All passwords encrypted with PBKDF2:SHA256 before insertion into SQLite. | 3 | Highest |
| **SCRUM-15** | Story | SCRUM-5 | User Login & Authentication Flow | Authenticate credentials; return generic error on mismatch to prevent enumeration. | 3 | Highest |
| **SCRUM-16** | Task | SCRUM-5 | Session Management & Login State | Establish session cookie with user_id, user_name, and user_email on successful login. | 2 | High |
| **SCRUM-17** | Task | SCRUM-5 | `@login_required` Route Protection Decorator | Unauthenticated requests to protected endpoints redirect to `/login` with flash notice. | 3 | High |
| **SCRUM-18** | Story | SCRUM-5 | Secure User Logout | Clear all session keys (`session.clear()`) and redirect to login page. | 1 | Medium |
| **SCRUM-19** | Task | SCRUM-5 | CSRF Token Generation in Sessions | Inject 32-byte cryptographically random CSRF token into user session. | 3 | Highest |
| **SCRUM-20** | Task | SCRUM-5 | Jinja Context Processor for Current User | Inject current user authentication state and name globally across all templates. | 1 | Low |

---

### Category B: Trusted Contacts & Safety Network (SCRUM-21 to SCRUM-30)

| Issue Key | Type | Epic Link | Summary | Acceptance Criteria | Story Points | Priority |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **SCRUM-21** | Story | SCRUM-6 | Add Trusted Emergency Contact | Form to add contact with full name, phone number, and relationship. | 3 | High |
| **SCRUM-22** | Task | SCRUM-6 | Contact Quota Boundary Check (Max 5) | Prevent insertion if user currently has >= 5 contacts; display warning notice. | 3 | High |
| **SCRUM-23** | Task | SCRUM-6 | UI Contact Quota Counter & Form Disabling | Display `X / 5 Contacts Configured` badge; disable form when limit is reached. | 2 | Medium |
| **SCRUM-24** | Task | SCRUM-6 | Contact Deletion with Ownership Verification | Delete route verifies `contact.user_id == session['user_id']`; return 403 on mismatch. | 3 | Highest |
| **SCRUM-25** | Story | SCRUM-6 | View Registered Trusted Contacts List | Render responsive table of contacts showing name, phone, relationship, and actions. | 2 | Medium |
| **SCRUM-26** | Task | SCRUM-6 | SQLite Schema for `trusted_contacts` Table | Create table with foreign key reference `user_id -> users(id) ON DELETE CASCADE`. | 2 | High |
| **SCRUM-27** | Task | SCRUM-6 | CSRF Protection for Contact Deletion | Form-based POST deletion protected with hidden CSRF token verification. | 2 | High |
| **SCRUM-28** | Story | SCRUM-6 | Confirmation Modal on Contact Removal | JavaScript confirm prompt before submitting contact deletion request. | 1 | Low |
| **SCRUM-29** | Task | SCRUM-6 | Phone Number Input Masking & Validation | Ensure contact phone numbers adhere to telephony format guidelines. | 2 | Medium |
| **SCRUM-30** | Task | SCRUM-6 | Relationship Categories Selection | Dropdown supporting Parent, Sibling, Spouse, Guardian, Friend, and Colleague. | 1 | Low |

---

### Category C: Location Sharing & Geolocation Telemetry (SCRUM-31 to SCRUM-33)

| Issue Key | Type | Epic Link | Summary | Acceptance Criteria | Story Points | Priority |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **SCRUM-31** | Story | SCRUM-7 | Browser HTML5 Geolocation API Integration | Automatically trigger `navigator.geolocation.getCurrentPosition` upon loading `/sos`. | 5 | Highest |
| **SCRUM-32** | Task | SCRUM-7 | Geolocation Error & Fallback Handler | Catch `PERMISSION_DENIED`, `POSITION_UNAVAILABLE`, and `TIMEOUT`; set status flags. | 3 | Highest |
| **SCRUM-33** | Task | SCRUM-7 | Manual Landmark Input Fallback | Text field allowing user to provide landmark notes when GPS is unavailable. | 2 | Medium |

---

### Category D: SOS Alerts & Incident Management (SCRUM-34 to SCRUM-38)

| Issue Key | Type | Epic Link | Summary | Acceptance Criteria | Story Points | Priority |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **SCRUM-34** | Story | SCRUM-8 | One-Tap SOS Distress Trigger Button | Prominent red circular button on `/sos` triggering emergency telemetry POST. | 5 | Highest |
| **SCRUM-35** | Story | SCRUM-8 | Simulated Broadcast to Trusted Contacts | System queries user's contacts and returns simulated SMS transmission payload. | 3 | High |
| **SCRUM-36** | Task | SCRUM-8 | SQLite Schema for `sos_alerts` Table | Create table storing `user_id`, timestamp, lat, lng, accuracy, status, and notes. | 2 | High |
| **SCRUM-37** | Story | SCRUM-9 | User Safety Dashboard Overview | Dashboard displaying greeting, contact count, quick SOS link, and recent alerts. | 3 | High |
| **SCRUM-38** | Task | SCRUM-9 | Recent SOS Incident Logs & Map Links | Table displaying last 5 alerts with clickable external Google Maps coordinate links. | 2 | Medium |

---

### Category E: Non-Functional & Security Engineering (SCRUM-39 to SCRUM-42)

| Issue Key | Type | Epic Link | Summary | Acceptance Criteria | Story Points | Priority |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **SCRUM-39** | Task | SCRUM-5 | Global `@verify_csrf` Request Interceptor | Decorator intercepting all modifying POST requests (form data and JSON headers). | 5 | Highest |
| **SCRUM-40** | Task | SCRUM-5 | Constant-Time CSRF Token Comparison | Prevent timing attacks via `secrets.compare_digest(token, expected_token)`. | 2 | High |
| **SCRUM-41** | Task | SCRUM-6 | SQLite Foreign Key Cascade Enforcement | Execute `PRAGMA foreign_keys = ON;` on every database connection. | 2 | High |
| **SCRUM-42** | Task | SCRUM-8 | Sub-Second Latency Optimization | Streamline JSON serialization and indexing for emergency dispatch endpoint. | 2 | Medium |

---

### Category F: Quality Assurance, Testing & PBL Documentation (SCRUM-43 to SCRUM-47)

| Issue Key | Type | Epic Link | Summary | Acceptance Criteria | Story Points | Priority |
| :--- | :--- | :--- | :--- | :--- | :---: | :--- |
| **SCRUM-43** | Test | SCRUM-10 | White-Box Unittest Suite (test_white_box.py) | Automated unittest file executing 20 internal code logic tests via Flask test client. | 5 | High |
| **SCRUM-44** | Test | SCRUM-10 | Black-Box Functional Test Matrix | 10 structured test cases in markdown covering auth, quota, ownership, and fallback. | 3 | High |
| **SCRUM-45** | Task | SCRUM-10 | PBL Final Project Report (Project_Report.md) | Academic report containing problem statement, requirements, schema, and future scope. | 5 | High |
| **SCRUM-46** | Task | SCRUM-10 | Responsive CSS Styling & Pulsing UI Animations | Bootstrap 5 + custom CSS theme with pulsing emergency SOS button. | 3 | Medium |
| **SCRUM-47** | Task | SCRUM-10 | National Emergency Hotline Banner Integration | Header bar rendering 24/7 emergency numbers (112 / 1091) across all templates. | 1 | Low |

---

### 3. Sprint Allocation Recommendation for Jira
- **Sprint 1 (Foundations & Auth):** `SCRUM-11` to `SCRUM-20`, `SCRUM-39`, `SCRUM-40`, `SCRUM-41` (Total: 26 Story Points)
- **Sprint 2 (Contacts & Quota Controls):** `SCRUM-21` to `SCRUM-30`, `SCRUM-26`, `SCRUM-27` (Total: 20 Story Points)
- **Sprint 3 (Geolocation, SOS & Telemetry):** `SCRUM-31` to `SCRUM-38`, `SCRUM-42` (Total: 25 Story Points)
- **Sprint 4 (Testing, Polish & PBL Report):** `SCRUM-43` to `SCRUM-47` (Total: 17 Story Points)

