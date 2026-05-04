"""
ProjectFlow — AI Client Project Management Platform
Features: Clients, Projects, AI Task Generation (OpenAI),
          Team Members, Task Assignment, Progress Tracking
Deployment: Vercel-ready (SQLite via /tmp for serverless)
"""

import sqlite3
import json
import os
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, jsonify
from openai import OpenAI

app = Flask(__name__)

# ─── Config ───────────────────────────────────────────────────────────────────
IS_VERCEL  = os.environ.get("VERCEL", False)
DATABASE   = "/tmp/database.db" if IS_VERCEL else os.path.join(os.path.dirname(__file__), "database.db")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# ─── Database ─────────────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                company TEXT,
                created_at TEXT DEFAULT (date('now'))
            );

            CREATE TABLE IF NOT EXISTS team_members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT,
                avatar_color TEXT DEFAULT '#4f7cff',
                created_at TEXT DEFAULT (date('now'))
            );

            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                deadline TEXT,
                created_at TEXT DEFAULT (date('now')),
                FOREIGN KEY (client_id) REFERENCES clients(id)
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                role TEXT NOT NULL,
                deadline TEXT,
                status TEXT DEFAULT 'Pending',
                notes TEXT DEFAULT '',
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );

            CREATE TABLE IF NOT EXISTS task_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                assigned_at TEXT DEFAULT (datetime('now')),
                UNIQUE(task_id, member_id),
                FOREIGN KEY (task_id) REFERENCES tasks(id),
                FOREIGN KEY (member_id) REFERENCES team_members(id)
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (project_id) REFERENCES projects(id)
            );
        ''')

# ─── AI Task Generation ────────────────────────────────────────────────────────

def generate_tasks_with_openai(project_title, project_description, project_deadline):
    """Generate tasks using OpenAI API."""
    if not OPENAI_API_KEY:
        raise ValueError("No OPENAI_API_KEY set")

    openai_client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""You are a senior project manager. Analyze this project and generate detailed tasks.

Project Title: {project_title}
Project Description: {project_description}
Project Deadline: {project_deadline}

Generate 8-12 specific, actionable tasks. Each task must be assigned to exactly one of:
- "UI Designer" — wireframes, layouts, user flows, prototypes, mockups
- "Graphic Designer" — logos, banners, illustrations, brand assets, icons
- "Developer" — backend, frontend, APIs, database, deployment, integrations

Rules:
- Make task titles SPECIFIC to this project, not generic
- Spread tasks across all 3 roles
- Set individual deadlines before or on {project_deadline}
- Vary the deadlines logically (design tasks come before dev tasks)

Return ONLY a raw JSON array, no markdown, no explanation, no code fences.

Example format:
[
  {{"title": "specific task name", "role": "UI Designer", "deadline": "YYYY-MM-DD"}},
  {{"title": "another task", "role": "Developer", "deadline": "YYYY-MM-DD"}}
]"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown fences if present
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("["):
                raw = part
                break

    # Extract JSON array
    start = raw.find("[")
    end   = raw.rfind("]") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    return json.loads(raw)

def generate_tasks_rule_based(project_title, project_description, deadline):
    """Smart rule-based fallback."""
    desc = (project_title + " " + project_description).lower()

    is_ecom  = any(w in desc for w in ['shop', 'store', 'ecommerce', 'shopify', 'woocommerce', 'cart'])
    is_app   = any(w in desc for w in ['app', 'mobile', 'ios', 'android', 'flutter'])
    is_brand = any(w in desc for w in ['brand', 'logo', 'identity', 'branding'])
    is_saas  = any(w in desc for w in ['saas', 'dashboard', 'platform', 'crm', 'software'])

    if is_ecom:
        ui  = ["Homepage wireframe", "Product listing page layout", "Checkout flow design"]
        gfx = ["Product banner designs", "Brand logo & favicon", "Promotional graphics"]
        dev = ["Store setup & configuration", "Payment gateway integration", "Inventory management system"]
    elif is_app:
        ui  = ["App onboarding screens", "Core feature wireframes", "Navigation & UX flow"]
        gfx = ["App icon & splash screen", "In-app illustrations", "Marketing screenshots"]
        dev = ["Backend API development", "Mobile app frontend", "App store deployment"]
    elif is_saas:
        ui  = ["Dashboard layout wireframe", "User settings screens", "Data visualization mockups"]
        gfx = ["Logo & brand assets", "Email template design", "Landing page graphics"]
        dev = ["Database schema & backend", "Authentication system", "Dashboard frontend & APIs"]
    elif is_brand:
        ui  = ["Brand style guide layout", "Website wireframe", "Presentation template"]
        gfx = ["Primary logo design", "Color palette & typography", "Business card design"]
        dev = ["Brand website development", "CMS setup", "SEO optimization"]
    else:
        ui  = ["Homepage wireframe", "Inner pages layout", "Mobile responsive mockups"]
        gfx = ["Logo & brand identity", "Hero banners", "Icon set design"]
        dev = ["Project setup & architecture", "Core feature development", "Testing & deployment"]

    tasks = []
    for t in ui:  tasks.append({"title": t, "role": "UI Designer",      "deadline": deadline})
    for t in gfx: tasks.append({"title": t, "role": "Graphic Designer", "deadline": deadline})
    for t in dev: tasks.append({"title": t, "role": "Developer",        "deadline": deadline})
    return tasks

# ─── Helpers ──────────────────────────────────────────────────────────────────

AVATAR_COLORS = ["#4f7cff","#7c5cfc","#22c98a","#f5a623","#f05252","#0ea5e9","#ec4899","#14b8a6"]

def compute_stats(project_id):
    today = date.today().isoformat()
    with get_db() as conn:
        tasks = conn.execute('SELECT * FROM tasks WHERE project_id = ?', (project_id,)).fetchall()
    total     = len(tasks)
    completed = sum(1 for t in tasks if t['status'] == 'Completed')
    overdue   = sum(1 for t in tasks if t['status'] != 'Completed' and t['deadline'] and t['deadline'] < today)
    pending   = total - completed - overdue
    progress  = int((completed / total) * 100) if total else 0
    return dict(total=total, completed=completed, overdue=overdue, pending=pending, progress=progress)

def get_task_assignments(task_id):
    with get_db() as conn:
        return conn.execute('''
            SELECT tm.* FROM team_members tm
            JOIN task_assignments ta ON ta.member_id = tm.id
            WHERE ta.task_id = ?
        ''', (task_id,)).fetchall()

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    today = date.today().isoformat()
    with get_db() as conn:
        clients  = conn.execute('SELECT * FROM clients ORDER BY created_at DESC').fetchall()
        projects = conn.execute('''
            SELECT p.*, c.name as client_name
            FROM projects p JOIN clients c ON p.client_id = c.id
            ORDER BY p.created_at DESC
        ''').fetchall()
        members  = conn.execute('SELECT * FROM team_members ORDER BY name').fetchall()
    stats = {p['id']: compute_stats(p['id']) for p in projects}
    return render_template('index.html', clients=clients, projects=projects,
                           stats=stats, members=members, today=today, colors=AVATAR_COLORS)

# ── Clients ──

@app.route('/client/add', methods=['POST'])
def add_client():
    name    = request.form.get('name','').strip()
    email   = request.form.get('email','').strip()
    company = request.form.get('company','').strip()
    if name:
        with get_db() as conn:
            conn.execute('INSERT INTO clients (name,email,company) VALUES (?,?,?)', (name,email,company))
    return redirect(url_for('index'))

@app.route('/client/<int:client_id>')
def client_view(client_id):
    today = date.today().isoformat()
    with get_db() as conn:
        client   = conn.execute('SELECT * FROM clients WHERE id=?', (client_id,)).fetchone()
        projects = conn.execute('SELECT * FROM projects WHERE client_id=?', (client_id,)).fetchall()
        feedback = conn.execute('''SELECT * FROM feedback WHERE project_id IN
            (SELECT id FROM projects WHERE client_id=?) ORDER BY created_at DESC''', (client_id,)).fetchall()
    if not client: return redirect(url_for('index'))
    stats = {p['id']: compute_stats(p['id']) for p in projects}
    return render_template('client_view.html', client=client, projects=projects,
                           stats=stats, feedback=feedback, today=today)

# ── Team Members ──

@app.route('/member/add', methods=['POST'])
def add_member():
    name  = request.form.get('name','').strip()
    role  = request.form.get('role','').strip()
    email = request.form.get('email','').strip()
    color = request.form.get('color', AVATAR_COLORS[0])
    if name and role:
        with get_db() as conn:
            conn.execute('INSERT INTO team_members (name,role,email,avatar_color) VALUES (?,?,?,?)',
                         (name, role, email, color))
    return redirect(url_for('index'))

@app.route('/member/<int:member_id>/delete', methods=['POST'])
def delete_member(member_id):
    with get_db() as conn:
        conn.execute('DELETE FROM task_assignments WHERE member_id=?', (member_id,))
        conn.execute('DELETE FROM team_members WHERE id=?', (member_id,))
    return redirect(url_for('index'))

# ── Projects ──

@app.route('/project/add', methods=['POST'])
def add_project():
    client_id   = request.form.get('client_id')
    title       = request.form.get('title','').strip()
    description = request.form.get('description','').strip()
    deadline    = request.form.get('deadline','')
    if not (client_id and title): return redirect(url_for('index'))

    with get_db() as conn:
        cur        = conn.execute('INSERT INTO projects (client_id,title,description,deadline) VALUES (?,?,?,?)',
                                  (client_id, title, description, deadline))
        project_id = cur.lastrowid

    try:
        tasks = generate_tasks_with_openai(title, description, deadline)
    except Exception as e:
        print(f"[OpenAI fallback] {e}")
        tasks = generate_tasks_rule_based(title, description, deadline)

    with get_db() as conn:
        for t in tasks:
            conn.execute('INSERT INTO tasks (project_id,title,role,deadline) VALUES (?,?,?,?)',
                         (project_id, t['title'], t['role'], t.get('deadline', deadline)))

    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/project/<int:project_id>')
def project_detail(project_id):
    today = date.today().isoformat()
    with get_db() as conn:
        project = conn.execute('''
            SELECT p.*, c.name as client_name, c.id as client_id
            FROM projects p JOIN clients c ON p.client_id=c.id WHERE p.id=?
        ''', (project_id,)).fetchone()
        if not project: return redirect(url_for('index'))
        tasks   = conn.execute('SELECT * FROM tasks WHERE project_id=? ORDER BY role,deadline',
                               (project_id,)).fetchall()
        members = conn.execute('SELECT * FROM team_members ORDER BY name').fetchall()

    # Attach assigned members to each task
    tasks_with_members = [{'task': t, 'assigned': get_task_assignments(t['id'])} for t in tasks]
    stats = compute_stats(project_id)
    return render_template('dashboard.html', project=project, tasks_with_members=tasks_with_members,
                           stats=stats, today=today, members=members)

# ── Tasks ──

@app.route('/task/<int:task_id>/toggle', methods=['POST'])
def toggle_task(task_id):
    with get_db() as conn:
        task       = conn.execute('SELECT * FROM tasks WHERE id=?', (task_id,)).fetchone()
        new_status = 'Completed' if task['status'] != 'Completed' else 'Pending'
        conn.execute('UPDATE tasks SET status=? WHERE id=?', (new_status, task_id))
        project_id = task['project_id']
    return redirect(request.referrer or url_for('project_detail', project_id=project_id))

@app.route('/task/add', methods=['POST'])
def add_task():
    project_id = request.form.get('project_id')
    title      = request.form.get('title','').strip()
    role       = request.form.get('role','Developer')
    deadline   = request.form.get('deadline','')
    if project_id and title:
        with get_db() as conn:
            conn.execute('INSERT INTO tasks (project_id,title,role,deadline) VALUES (?,?,?,?)',
                         (project_id, title, role, deadline))
    return redirect(url_for('project_detail', project_id=project_id))

@app.route('/task/<int:task_id>/assign-bulk', methods=['POST'])
def assign_bulk(task_id):
    """Save member assignments for a task (checkbox form)."""
    project_id   = request.form.get('project_id')
    selected_ids = request.form.getlist('member_ids')
    with get_db() as conn:
        conn.execute('DELETE FROM task_assignments WHERE task_id=?', (task_id,))
        for mid in selected_ids:
            try:
                conn.execute('INSERT INTO task_assignments (task_id,member_id) VALUES (?,?)', (task_id, mid))
            except Exception:
                pass
    return redirect(url_for('project_detail', project_id=project_id))

# ── Feedback ──

@app.route('/feedback/add', methods=['POST'])
def add_feedback():
    project_id = request.form.get('project_id')
    message    = request.form.get('message','').strip()
    if project_id and message:
        with get_db() as conn:
            conn.execute('INSERT INTO feedback (project_id,message) VALUES (?,?)', (project_id, message))
            project = conn.execute('SELECT client_id FROM projects WHERE id=?', (project_id,)).fetchone()
        if project: return redirect(url_for('client_view', client_id=project['client_id']))
    return redirect(url_for('index'))

# ── API ──

@app.route('/api/stats/<int:project_id>')
def api_stats(project_id):
    return jsonify(compute_stats(project_id))

# ─── Bootstrap ────────────────────────────────────────────────────────────────
init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
