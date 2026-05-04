# ProjectFlow — AI Client Project Management Platform

## Quick Start (under 2 minutes)

```bash
cd projectflow
pip install -r requirements.txt
python app.py
```

Then open: http://localhost:5000

## Features
- Add clients, create projects, auto-generate tasks via AI (Claude) or rule-based fallback
- Tasks assigned to UI Designer / Graphic Designer / Developer
- Progress bars, overdue detection, color-coded status
- Client portal with feedback form

## AI Task Generation
Needs ANTHROPIC_API_KEY env variable for AI generation. Falls back to smart rule-based generation automatically.

```bash
export ANTHROPIC_API_KEY=sk-ant-...
python app.py
```

## File Structure
```
projectflow/
├── app.py              # Flask routes + DB logic
├── requirements.txt    # flask, anthropic
├── static/style.css    # Dark editorial CSS
└── templates/
    ├── index.html      # Main dashboard
    ├── dashboard.html  # Project detail + tasks
    └── client_view.html # Client portal
```
