# AI_PROJECT_MANAGER
# 🚀 ProjectFlow — AI Client Project Management Platform
ProjectFlow is an **AI-powered project management system** that automates how companies handle client projects — from onboarding to task generation, assignment, tracking, and feedback.
It helps teams break down complex projects into structured tasks using AI and provides clients with a **real-time progress dashboard**.
---

## ✨ Features

### 👤 Client Management

* Add and manage multiple clients
* Dedicated client portal to track project progress
* View deadlines, completion %, and task status

### 🤖 AI Task Generation

* Automatically converts project requirements into actionable tasks
* Categorizes tasks into:

  * 🎨 UI Designer
  * ✏️ Graphic Designer
  * 💻 Developer
* Smart deadline distribution

### 📊 Progress Tracking

* Real-time progress bars
* Completed / Pending / Overdue task tracking
* Visual indicators for project health

### 👥 Team Management

* Add team members with roles
* Assign tasks to individuals
* Avatar-based team visualization

### 💬 Feedback System

* Clients can submit feedback per project
* Transparent communication between client & company

### ⚡ Reliable Fallback System

* If AI fails → system auto-generates tasks using rule-based logic
* Ensures uninterrupted workflow

---

## 🧠 How It Works

```text
Client → Project Created → AI Generates Tasks → Tasks Assigned → Progress Tracked → Client Feedback
```

---

## 🛠️ Tech Stack

* **Backend:** Python, Flask
* **Frontend:** HTML, CSS (Custom UI)
* **Database:** SQLite
* **AI Integration:** OpenAI API
* **Deployment:** Vercel (Serverless Ready)

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/projectflow.git
cd projectflow
```

---

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3️⃣ Set OpenAI API Key

#### 🔹 Option 1: Environment Variable

**Mac/Linux**

```bash
export OPENAI_API_KEY=sk-xxxxx
```

**Windows**

```bash
set OPENAI_API_KEY=sk-xxxxx
```

---

#### 🔹 Option 2: `.env` file

Create `.env` file:

```env
OPENAI_API_KEY=sk-xxxxx
```

Add this in `app.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

---

### 4️⃣ Run the App

```bash
python app.py
```

---

### 5️⃣ Open in Browser

```
http://localhost:5000
```

---

## 🌐 Deployment (Vercel)

1. Push project to GitHub
2. Import into Vercel
3. Add environment variable:

```
OPENAI_API_KEY = sk-xxxxx
```

4. Deploy 🚀

---

## 📂 Project Structure

```
projectflow/
│
├── app.py                # Backend logic + routes
├── requirements.txt      # Dependencies
├── database.db           # SQLite database
│
├── templates/
│   ├── index.html        # Dashboard
│   ├── dashboard.html    # Project detail
│   └── client_view.html  # Client portal
│
├── static/
│   └── style.css         # UI styling
│
└── vercel.json           # Deployment config
```

---

## 🧪 Usage

1. Add a client
2. Create a project with description
3. AI generates tasks automatically
4. Assign tasks to team members
5. Track progress in dashboard
6. Client views progress & submits feedback

---

## ⚠️ Important Notes

* Do not hardcode API keys
* Always use environment variables
* Requires OpenAI billing enabled

---
