# Project-Based Learning (PBL) Final Project Report

---

# WOMEN SAFETY MANAGEMENT SYSTEM (WSMS)
### A Web-Based Emergency Telemetry & Distress Response Platform
**Course:** Software Engineering (CS-301) &bull; 5th Semester B.Tech  
**Project Type:** Academic Project-Based Learning (PBL) Prototype  
**Date:** Academic Year 2026  

---

## 1. Project Title, Problem Statement & Objectives

### 1.1 Project Title
**Women Safety Management System (WSMS)**: A High-Availability Emergency Geolocation Telemetry, Rapid Distress Dispatch, and Trusted Contact Management Platform.

### 1.2 Problem Statement
Personal safety in urban and semi-urban transit environments remains an urgent social and technical challenge for women, students, and vulnerable commuters. Existing safety solutions often suffer from severe usability friction:
1. **Excessive Latency:** Commercial emergency applications often require navigating complex multi-level menus, unlocking biometric interfaces, or launching heavy native apps that crash under low-memory or degraded connectivity conditions.
2. **Lack of Fallback Geolocation Handling:** Many mobile systems fail completely when a user inadvertently disables GPS or when satellite lock is obstructed by high-rise buildings, underground metro stations, or concrete interiors.
3. **Absence of Strict Access & Data Ownership Checks:** Incident data and trusted contact circles are often managed insecurely without cross-user ownership isolation or token-based request protection, leaving user data vulnerable to scraping and tampering.
4. **Information Asymmetry during Crisis:** When distress signals are triggered, recipients rarely receive immediate actionable context (e.g., precise coordinates, timestamp, landmark notes, and battery/connection telemetry) simultaneously.

### 1.3 Project Objectives
The overarching goal of the WSMS project is to engineer a resilient, lightweight, responsive, and secure web application capable of immediate emergency alert dispatching. The specific engineering objectives are:
- **Instant SOS Triggering:** Provide a prominent, one-tap distress button accessible across mobile and desktop browsers with minimal user interaction steps.
- **Resilient Geolocation Telemetry with Fallback:** Exploit the W3C HTML5 Geolocation API to acquire high-accuracy latitude and longitude coordinates, while seamlessly degrading to manual landmark and network fallback modes when sensors are denied or unavailable.
- **Enforced Contact Boundaries:** Enable users to curate a personal safety circle of up to five (5) trusted emergency contacts, protected by strict database ownership controls and CSRF tokens.
- **Audit Logging & Incident Persistence:** Record every distress event in an SQLite relational database with precise UTC timestamps, telemetry status, coordinates, and notification histories.
- **Enterprise-Grade Web Security:** Implement industry-standard security mechanisms, including PBKDF2/scrypt password hashing (via Werkzeug), session fixation mitigation, parameterization against SQL injection, and cryptographically random CSRF validation tokens.

---

## 2. Requirements Analysis

The software requirements have been engineered following standard IEEE 830 / Agile Software Engineering guidelines and mapped to the Jira project backlog tracking items (**SCRUM-11** through **SCRUM-47**).

### 2.1 Functional Requirements (FR-01 to FR-12)

| Req ID | Functional Requirement Description | Jira Task Mapping | Acceptance Criteria |
| :--- | :--- | :--- | :--- |
| **FR-01** | **User Registration & Validation**<br>The system shall permit new users to register with full name, email, phone number, and password. Empty inputs and passwords under 8 characters must be strictly rejected. | `SCRUM-11`<br>`SCRUM-12` | Returns HTTP 400 with user-friendly validation notices if inputs are missing or password < 8 characters. |
| **FR-02** | **Unique Identity Enforcement**<br>The system shall enforce email address uniqueness during registration to avoid duplicate identity creation. | `SCRUM-13` | Duplicate email attempts trigger HTTP 400 with message *"An account with this email address already exists."* |
| **FR-03** | **Secure Credential Authentication**<br>The system shall authenticate users using PBKDF2:SHA256 password hash comparison without storing or logging plain-text passwords. | `SCRUM-14`<br>`SCRUM-15` | All passwords stored in database as salted hashes. Generic error returned on failure to prevent user enumeration. |
| **FR-04** | **Session & Access Control**<br>The system shall restrict protected application routes (`/dashboard`, `/trusted-contacts`, `/sos`) to authenticated sessions only. | `SCRUM-16`<br>`SCRUM-17` | Unauthenticated visits redirect to `/login?next=<path>` with an informational flash notification. |
| **FR-05** | **Trusted Contact Creation**<br>The system shall allow users to register emergency contacts with name, phone number, and familial/social relationship. | `SCRUM-21` | Form requires valid name, phone, and relationship category before database insertion. |
| **FR-06** | **Trusted Contact Quota Enforcement**<br>The system shall enforce an upper ceiling of five (5) trusted contacts per registered user. | `SCRUM-22`<br>`SCRUM-23` | System inspects existing contact count. Attempting to add a 6th contact is blocked with a limit alert. |
| **FR-07** | **Contact Ownership Isolation**<br>The system shall enforce strict authorization checks such that a user can only view and delete their own trusted contacts. | `SCRUM-24` | Attempting to delete another user's contact record returns HTTP 403 Forbidden. |
| **FR-08** | **HTML5 Geolocation Acquisition**<br>The system shall automatically request browser GPS coordinates with high accuracy upon loading the SOS console. | `SCRUM-31` | Latitude, longitude, and accuracy radius are captured via `navigator.geolocation.getCurrentPosition`. |
| **FR-09** | **GPS Fallback Protocol**<br>The system shall detect geolocation denial, sensor unavailability, or timeout, gracefully transitioning to manual landmark mode. | `SCRUM-32`<br>`SCRUM-33` | Sets telemetry status to `DENIED`, `UNAVAILABLE`, or `TIMEOUT`, captures optional manual landmark notes, and proceeds without crashing. |
| **FR-10** | **Emergency SOS Alert Persistence**<br>The system shall record all SOS triggers into SQLite with `user_id`, UTC timestamp, coordinates, telemetry status, and notes. | `SCRUM-34` | Alert record assigned unique auto-incrementing ID and stored in `sos_alerts` table. |
| **FR-11** | **Distress Broadcast Simulation**<br>The system shall simulate an SMS/telephony dispatch to all registered contacts upon SOS trigger, displaying transmission telemetry. | `SCRUM-35` | UI updates with real-time dispatch receipt showing names, phone numbers, and simulated SMS delivery. |
| **FR-12** | **Incident History & Audit Dashboard**<br>The system shall display recent SOS events on the dashboard with direct links to Google Maps coordinates. | `SCRUM-37`<br>`SCRUM-38` | Dashboard table presents latest 5 incidents with color-coded status badges and external map links. |

### 2.2 Non-Functional Requirements (NFR-01 to NFR-07)

| Req ID | Category | Non-Functional Requirement Description | Jira Task Mapping | Metric / Standard |
| :--- | :--- | :--- | :--- | :--- |
| **NFR-01** | **Security** | The system must protect all state-modifying requests (POST) against Cross-Site Request Forgery (CSRF). | `SCRUM-39`<br>`SCRUM-40` | Cryptographically generated 32-byte session token; rejected with HTTP 400 if missing or mismatched. |
| **NFR-02** | **Data Integrity** | Foreign key constraints and cascade rules must be strictly enforced at the database engine level. | `SCRUM-41` | `PRAGMA foreign_keys = ON;` enabled; orphan records purged automatically on user account deletion. |
| **NFR-03** | **Performance** | SOS alert submission and telemetry processing must complete within sub-second latency. | `SCRUM-42` | Server response latency < 350 ms under local execution; lightweight JSON payloads (< 2 KB). |
| **NFR-04** | **Usability** | The emergency panic button must be instantly discoverable and require no more than one tap to trigger. | `SCRUM-43` | Visual prominence with contrasting crimson color (#dc2626), pulsing CSS animation, and diameter >= 200px on mobile. |
| **NFR-05** | **Availability & Resilience** | The application must remain operable even if hardware GPS sensors or satellite fixes fail. | `SCRUM-44` | Complete graceful degradation to manual landmark notes; zero fatal unhandled JavaScript or Python exceptions. |
| **NFR-06** | **Maintainability** | Codebase must maintain modular separation between presentation templates, routes, and database access. | `SCRUM-45` | Clean MVC structure using Flask application context, Jinja2 inheritance, and isolated unittest suite. |
| **NFR-07** | **Portability** | The web application must render responsively across mobile, tablet, and desktop viewports. | `SCRUM-46`<br>`SCRUM-47` | Fully responsive design compliant with Bootstrap 5 viewport grid across screen widths >= 320px. |

---

## 3. System Architecture & Workflow

### 3.1 Architectural Overview
The Women Safety Management System follows a classic 3-Tier Model:

```
[ Client Presentation Tier ]
   │  - HTML5 / CSS3 (Bootstrap 5, Custom Pulse Theme)
   │  - JavaScript W3C Geolocation API & AJAX Fetch Telemetry
   │  - CSRF Header & Form Injection
   ▼
[ Application Logic Tier (Flask Backend) ]
   │  - WSGI Request Handler (app.py)
   │  - Security & CSRF Token Verification Interceptor (@verify_csrf)
   │  - Session & Authentication Guard (@login_required)
   │  - Telemetry & Fallback Parser Engine
   │  - Contact Quota & Ownership Validator
   ▼
[ Data Persistence Tier (SQLite Database) ]
   │  - Schema with Foreign Key Cascade Constraints (PRAGMA foreign_keys = ON)
   │  - Tables: users, trusted_contacts, sos_alerts
   │  - Atomic Transaction Commits
```

### 3.2 Relational Database Schema & Data Dictionary

#### 1. `users` Table
Stores authenticated account credentials and default safety preferences.
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT — Unique user identifier.
- `name`: TEXT NOT NULL — User's legal full name.
- `email`: TEXT UNIQUE NOT NULL — Account email, indexed for rapid login lookups.
- `phone`: TEXT NOT NULL — Primary telephone contact.
- `password_hash`: TEXT NOT NULL — PBKDF2:SHA256 encrypted password digest.
- `emergency_message`: TEXT DEFAULT 'Emergency! I need immediate help...' — Custom message template.
- `created_at`: DATETIME DEFAULT CURRENT_TIMESTAMP — Account creation timestamp.

#### 2. `trusted_contacts` Table
Stores pre-approved emergency recipients tied to specific users.
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT — Unique contact record identifier.
- `user_id`: INTEGER NOT NULL — Foreign key referencing `users(id)` ON DELETE CASCADE.
- `contact_name`: TEXT NOT NULL — Recipient name.
- `contact_phone`: TEXT NOT NULL — Recipient phone number (E.164 formatted).
- `relationship`: TEXT NOT NULL — Relationship classification (e.g., Parent, Sibling, Friend).
- `created_at`: DATETIME DEFAULT CURRENT_TIMESTAMP — Timestamp when contact was registered.

#### 3. `sos_alerts` Table
Immutable historical audit trail of all distress signals triggered through the platform.
- `id`: INTEGER PRIMARY KEY AUTOINCREMENT — Unique distress incident number.
- `user_id`: INTEGER NOT NULL — Foreign key referencing `users(id)` ON DELETE CASCADE.
- `timestamp`: DATETIME DEFAULT CURRENT_TIMESTAMP — Exact UTC distress invocation time.
- `latitude`: REAL NULLABLE — WGS84 GPS Latitude coordinate.
- `longitude`: REAL NULLABLE — WGS84 GPS Longitude coordinate.
- `accuracy`: REAL NULLABLE — GPS accuracy radius in meters.
- `location_status`: TEXT NOT NULL — Telemetry status: `'ACQUIRED'`, `'DENIED'`, `'UNAVAILABLE'`, `'TIMEOUT'`, or `'MANUAL_FALLBACK'`.
- `emergency_notes`: TEXT NULLABLE — Optional user landmark or contextual distress notes.
- `status`: TEXT DEFAULT 'ACTIVE' — Lifecycle flag for emergency management.

### 3.3 Emergency SOS Execution Flow

```
[ User Presses "SEND SOS" Button ]
               │
               ▼
   [ Browser Geolocation Sensor Check ]
          /                 \
         / (Permission Granted) \ (Denied or Unavailable)
        ▼                         ▼
[ Capture Lat / Lng / Accuracy ]   [ Set Status = 'DENIED'/'UNAVAILABLE' ]
[ Status = 'ACQUIRED' ]            [ Capture Optional Landmark Notes ]
        \                         /
         \                       /
          ▼                     ▼
[ Pack JSON Payload + Embed Session CSRF Token ]
               │
               ▼
[ HTTP POST /sos Dispatched to Flask Server ]
               │
               ▼
[ Verify Session & Validate CSRF Token Header ]
       ├── (Invalid Token) ──► Return HTTP 400 Bad Request
       │
       └── (Valid Token)
               │
               ▼
[ Extract & Sanitize Telemetry Data ]
               │
               ▼
[ Insert Record into SQLite 'sos_alerts' Table ]
               │
               ▼
[ Query User's Registered Trusted Contacts (Max 5) ]
               │
               ▼
[ Generate Notification Dispatch Simulation Payload ]
               │
               ▼
[ Return HTTP 200 OK with Incident ID & Telemetry Summary ]
               │
               ▼
[ Client UI Renders Real-Time Confirmation & Audit Link ]
```

---

## 4. Security Engineering & Defensive Design

1. **Cryptographic Password Storage:** Plaintext passwords are never stored. The system employs Werkzeug's implementation of PBKDF2 with SHA-256 (and salt rounds), rendering offline dictionary attacks computationally prohibitive.
2. **Double-Submit / Session CSRF Token Defense:** Every modifying POST operation requires a 32-byte cryptographically random token (`secrets.token_hex(32)`) matched against the server-side session using constant-time string comparison (`secrets.compare_digest`), preventing Cross-Site Request Forgery.
3. **Session Fixation & Hijacking Prevention:** Sessions are cleared and regenerated upon login (`session.clear()`), preventing attackers from fixing session tokens prior to authentication.
4. **SQL Injection Immunization:** All database operations utilize parameterized queries with positional placeholders (`?`), completely isolating user inputs from the SQLite query compilation engine.
5. **Ownership & Access Control Verification:** In `delete_trusted_contact`, the application strictly verifies that the record's `user_id` matches the authenticated `session['user_id']`. An unauthorized request returns HTTP 403 Forbidden.

---

## 5. Limitations & Future Scope

### 5.1 Current Prototype Limitations
- **Simulated Notification Dispatch:** In this academic prototype, the dispatch of SMS alerts is simulated via real-time telemetry rendering and server logging, as commercial SMS gateway APIs (e.g., Twilio, AWS SNS) require paid subscriptions and carrier verification.
- **Single-Host SQLite Database:** SQLite is utilized for zero-configuration persistence. While optimal for single-node testing and academic evaluations, high-concurrency production deployments would require PostgreSQL or MySQL with connection pooling.
- **Client-Side Geolocation Dependency:** Coordinates rely on the client device's browser permissions and cellular/satellite triangulation capabilities.

### 5.2 Future Enhancements
- **Live SMS/Telephony Gateway Integration:** Integrate Twilio or Infobip REST APIs to transmit immediate SMS alerts with clickable Google Maps short-links directly to recipients' cellular phones.
- **Real-Time WebSockets GPS Tracking:** Implement Flask-SocketIO to enable continuous, live breadcrumb tracking of the user's movement while the SOS incident remains active.
- **Hardware IoT Panic Button Integration:** Connect external Bluetooth Low Energy (BLE) smart rings, wristbands, or physical pendant buttons to trigger the `/sos` endpoint without touching the phone screen.
- **Safe Route Recommendation & Geofencing:** Utilize OpenStreetMap and local crime mapping APIs to alert users when entering low-safety or poorly-lit corridors.

---

## 6. Academic Conclusion
The Women Safety Management System (WSMS) successfully fulfills all core requirements established under academic Project-Based Learning (PBL) standards for Software Engineering. By combining rigorous security controls, resilient geolocation fallback logic, strict relational quota constraints, and comprehensive test suites, the application demonstrates production-ready architectural principles in a clean, maintainable web platform.

