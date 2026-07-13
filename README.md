# Placement Portal Application (PPA) - V2

A web application to manage campus recruitment. Students can apply for drives, Companies can manage applicants, and Admin can oversee the entire process.

## Tech Stack
- **Backend:** Flask (Python)
- **Frontend:** Vue.js 3 + Bootstrap 5
- **Database:** SQLite
- **Automation:** Celery + Redis
- **Mail Testing:** MailHog

---

## How to Run the Project

To run the full application, you need to open **6 separate terminals**.

### 1. Redis Server
Ensure you have Redis installed.
```bash
redis-server
```

### 2. MailHog
Required for capturing emails (Registration, Reminders, Reports).
```bash
mailhog
```

### 3. Backend (Flask)
```bash
cd Backend
# Recommended: Create a virtual environment
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```
*API runs at: http://localhost:5001*

### 4. Frontend (Vue.js)
```bash
cd Frontend
npm install
npm run serve
```
*Frontend runs at: http://localhost:8080*

### 5. Celery Worker (Background Tasks)
```bash
# In Backend folder
python -m celery -A app.celery worker --loglevel=info -P solo
```

### 6. Celery Beat (Scheduled Jobs)
```bash
# In Backend folder
python -m celery -A app.celery beat --loglevel=info
```

---

## Default Credentials

### Admin Login
- **Email:** `admin@gmail.com`
- **Password:** `1234`
*(Admin is automatically created on first run)*

---

## Main Features

###  Student
- Search and apply for placement drives.
- Track application status (Applied / Shortlisted / Selected / Rejected).
- Upload Resume (PDF).
- Export application history as CSV (sent via email).

###  Company
- Create placement drives.
- View and manage applicants (Update status, set interview dates).
- Wait for Admin approval for registration and drives.

###  Admin
- Approve/Reject company registrations and placement drives.
- Manage all students and companies (Deactivate or Blacklist).
- View dashboard statistics.
- Automatically receive Monthly Placement Reports.

---

## Background Jobs (Celery + MailHog)
- **Daily Reminders:** Runs every 6 minutes (for demo purposes) to remind students of upcoming deadlines.
- **Monthly Reports:** Runs on the 1st of every month to send stats to Admin.
- **CSV Export:** Triggered manually by student, file is sent via email.
- **Email UI:** Access http://localhost:8025 to see all emails sent by the system.

---

## Folder Structure
```text
.
├── Backend/
│   ├── api/            # Route handlers
│   ├── app.py          # Main entry point
│   ├── models.py       # Database models
│   ├── tasks.py        # Celery tasks
│   └── instance/       # SQLite DB location
└── Frontend/
    └── src/            # Vue pages and logic
```
