from flask import Flask, request, jsonify, render_template_string, redirect, url_for, session
from flask_cors import CORS
import sqlite3
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'apex_fitness_secret_2026'  # Change this to a random secret in production
CORS(app)

DB_PATH = 'apex_fitness.db'

# ─── Database Setup ────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name   TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            phone       TEXT,
            plan        TEXT    NOT NULL DEFAULT 'pro',
            password    TEXT    NOT NULL,
            joined_at   TEXT    NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database ready: apex_fitness.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─── API: Register (Join Form) ─────────────────────────────────────────────────

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()

    full_name = data.get('fullName', '').strip()
    email     = data.get('email', '').strip().lower()
    phone     = data.get('phone', '').strip()
    plan      = data.get('plan', 'pro').strip()
    password  = data.get('password', '').strip()

    if not full_name or not email or not password:
        return jsonify({'success': False, 'message': 'Name, email and password are required.'}), 400

    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters.'}), 400

    try:
        conn = get_db()
        conn.execute(
            'INSERT INTO members (full_name, email, phone, plan, password, joined_at) VALUES (?, ?, ?, ?, ?, ?)',
            (full_name, email, phone, plan, hash_password(password), datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': f'Welcome to Apex Fitness, {full_name}! 🎉'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'This email is already registered.'}), 409

# ─── API: Login ────────────────────────────────────────────────────────────────

@app.route('/api/login', methods=['POST'])
def login():
    data     = request.get_json()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()

    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400

    conn   = get_db()
    member = conn.execute(
        'SELECT * FROM members WHERE email = ? AND password = ?',
        (email, hash_password(password))
    ).fetchone()
    conn.close()

    if member:
        return jsonify({
            'success': True,
            'message': f'Welcome back, {member["full_name"]}!',
            'member': {
                'id':        member['id'],
                'full_name': member['full_name'],
                'email':     member['email'],
                'plan':      member['plan'],
                'joined_at': member['joined_at']
            }
        })
    return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

# ─── Admin Dashboard ───────────────────────────────────────────────────────────

ADMIN_PASSWORD = 'admin123'   # ← Change this!

ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Apex Fitness — Admin</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root { --bg:#0a0a0a; --bg-card:rgba(12,10,20,0.9); --text:#f0f0f5; --muted:#9a95a8;
            --accent:#7c3aed; --accent-light:#a855f7; --border:rgba(168,85,247,0.2); }
    * { margin:0; padding:0; box-sizing:border-box; }
    body { font-family:'Inter',sans-serif; background:var(--bg); color:var(--text); min-height:100vh; }

    /* Login */
    .login-wrap { display:flex; align-items:center; justify-content:center; min-height:100vh; }
    .login-card { background:var(--bg-card); border:1.5px solid var(--border); border-radius:18px;
                  padding:2.8rem 2.4rem; width:360px; }
    .login-card h2 { font-size:1.5rem; font-weight:700; margin-bottom:0.4rem; }
    .login-card p  { color:var(--muted); font-size:0.88rem; margin-bottom:2rem; }

    /* Dashboard */
    .dash-wrap { max-width:1100px; margin:0 auto; padding:2.5rem 2rem; }
    .dash-header { display:flex; justify-content:space-between; align-items:center; margin-bottom:2rem; }
    .dash-header h1 { font-size:1.8rem; font-weight:800; }
    .dash-header h1 span { background:linear-gradient(135deg,var(--accent-light),#c084fc);
                           -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
    .stats { display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; margin-bottom:2rem; }
    .stat-card { background:var(--bg-card); border:1px solid var(--border); border-radius:14px;
                 padding:1.4rem 1.6rem; }
    .stat-card .num { font-size:2rem; font-weight:800; color:var(--accent-light); }
    .stat-card .lbl { color:var(--muted); font-size:0.8rem; text-transform:uppercase; letter-spacing:1px; margin-top:0.2rem; }

    table { width:100%; border-collapse:collapse; background:var(--bg-card);
            border:1px solid var(--border); border-radius:14px; overflow:hidden; }
    thead th { background:rgba(124,58,237,0.15); padding:0.9rem 1.2rem; text-align:left;
               font-size:0.75rem; text-transform:uppercase; letter-spacing:1px; color:var(--muted); }
    tbody td { padding:0.9rem 1.2rem; border-top:1px solid rgba(255,255,255,0.04);
               font-size:0.88rem; }
    tbody tr:hover { background:rgba(124,58,237,0.05); }

    .badge { display:inline-block; padding:0.2rem 0.75rem; border-radius:50px; font-size:0.72rem;
             font-weight:600; text-transform:uppercase; letter-spacing:0.5px; }
    .badge-basic { background:rgba(255,255,255,0.07); color:var(--muted); }
    .badge-pro   { background:rgba(124,58,237,0.2); color:#a855f7; border:1px solid rgba(168,85,247,0.3); }
    .badge-elite { background:rgba(234,179,8,0.15); color:#fbbf24; border:1px solid rgba(234,179,8,0.3); }

    label { display:block; font-size:0.78rem; font-weight:600; color:var(--muted);
            text-transform:uppercase; letter-spacing:1px; margin-bottom:0.4rem; }
    input[type=password] { width:100%; padding:0.85rem 1rem; border-radius:12px;
            border:1.5px solid var(--border); background:rgba(255,255,255,0.03);
            color:var(--text); font-family:'Inter',sans-serif; font-size:0.95rem;
            outline:none; margin-bottom:1.2rem; }
    input[type=password]:focus { border-color:var(--accent-light); }
    .btn { display:inline-block; padding:0.85rem 2rem; border-radius:50px; font-size:0.88rem;
           font-weight:600; cursor:pointer; border:none; font-family:'Inter',sans-serif;
           text-decoration:none; letter-spacing:0.5px; }
    .btn-primary { background:linear-gradient(135deg,var(--accent),var(--accent-light)); color:#fff; }
    .btn-outline  { background:transparent; color:var(--accent-light);
                    border:1.5px solid var(--accent-light); }
    .error { color:#f87171; font-size:0.85rem; margin-bottom:1rem; }
    .empty { text-align:center; color:var(--muted); padding:3rem; }
  </style>
</head>
<body>

{% if not logged_in %}
<div class="login-wrap">
  <div class="login-card">
    <h2>Admin <span style="background:linear-gradient(135deg,#a855f7,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">Panel</span></h2>
    <p>Apex Fitness — Members Dashboard</p>
    {% if error %}<p class="error">{{ error }}</p>{% endif %}
    <form method="POST" action="/admin">
      <label>Admin Password</label>
      <input type="password" name="password" placeholder="Enter admin password" autofocus>
      <button type="submit" class="btn btn-primary" style="width:100%">Login</button>
    </form>
  </div>
</div>

{% else %}
<div class="dash-wrap">
  <div class="dash-header">
    <h1>APEX <span>FITNESS</span> — Members</h1>
    <a href="/admin/logout" class="btn btn-outline">Logout</a>
  </div>

  <div class="stats">
    <div class="stat-card"><div class="num">{{ total }}</div><div class="lbl">Total Members</div></div>
    <div class="stat-card"><div class="num">{{ basic }}</div><div class="lbl">Basic Plan</div></div>
    <div class="stat-card"><div class="num">{{ pro }}</div><div class="lbl">Pro Plan</div></div>
    <div class="stat-card"><div class="num">{{ elite }}</div><div class="lbl">Elite Plan</div></div>
  </div>

  {% if members %}
  <table>
    <thead>
      <tr>
        <th>#</th><th>Name</th><th>Email</th><th>Phone</th><th>Plan</th><th>Joined</th>
      </tr>
    </thead>
    <tbody>
      {% for m in members %}
      <tr>
        <td>{{ m.id }}</td>
        <td>{{ m.full_name }}</td>
        <td>{{ m.email }}</td>
        <td>{{ m.phone or '—' }}</td>
        <td><span class="badge badge-{{ m.plan }}">{{ m.plan }}</span></td>
        <td>{{ m.joined_at }}</td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <div class="empty">No members yet. Share your website to get signups!</div>
  {% endif %}
</div>
{% endif %}

</body>
</html>
'''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('password') == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect('/admin')
        return render_template_string(ADMIN_TEMPLATE, logged_in=False, error='Wrong password.')

    if not session.get('admin'):
        return render_template_string(ADMIN_TEMPLATE, logged_in=False, error=None)

    conn    = get_db()
    members = conn.execute('SELECT * FROM members ORDER BY joined_at DESC').fetchall()
    counts  = conn.execute("SELECT plan, COUNT(*) as c FROM members GROUP BY plan").fetchall()
    conn.close()

    plan_map = {r['plan']: r['c'] for r in counts}
    return render_template_string(
        ADMIN_TEMPLATE,
        logged_in=True,
        members=members,
        total=len(members),
        basic=plan_map.get('basic', 0),
        pro=plan_map.get('pro', 0),
        elite=plan_map.get('elite', 0)
    )

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/admin')

# ─── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    print("🚀 Apex Fitness backend running at http://localhost:5000")
    print("📋 Admin panel: http://localhost:5000/admin")
    app.run(debug=True, port=5000)
