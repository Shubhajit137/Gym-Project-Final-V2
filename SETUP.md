# Apex Fitness — Backend Setup Guide

## What's included
- `app.py`        → Flask server (handles register, login, admin panel)
- `requirements.txt` → Python packages needed
- `join.html`     → Updated join page (replace your existing one)

The database file `apex_fitness.db` is created automatically when you first run the server.

---

## Step 1 — Install Python packages

Open a terminal in this folder and run:

```
pip install -r requirements.txt
```

---

## Step 2 — Start the server

```
python app.py
```

You should see:
```
✅ Database ready: apex_fitness.db
🚀 Apex Fitness backend running at http://localhost:5000
📋 Admin panel: http://localhost:5000/admin
```

Keep this terminal open while using the website.

---

## Step 3 — Replace your join.html

Copy the new `join.html` from this folder into your website folder,
replacing the old one.

---

## Step 4 — Open your website

Open `index.html` in your browser as usual. The Join page will now:
- Save new member registrations to the SQLite database
- Allow returning members to log in
- Show a success/error message after each action

---

## Admin Panel

Go to: http://localhost:5000/admin

Default password: **admin123**

⚠️ Change this in app.py → look for: ADMIN_PASSWORD = 'admin123'

The admin panel shows:
- Total member count by plan (Basic / Pro / Elite)
- Full table of all registered members

---

## Database location

The file `apex_fitness.db` is created in the same folder as `app.py`.
You can open it with any SQLite viewer (e.g. DB Browser for SQLite).

Table: **members**
Columns: id, full_name, email, phone, plan, password (hashed), joined_at
