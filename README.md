# StudyPlanner Dashboard

## Requirements
- Python 3.9+
- Flask

## Run
1. Extract the ZIP.
2. Open the `study_planner_dashboard` folder in VS Code.
3. Open Terminal in that folder.
4. Install Flask: `python -m pip install flask`
5. Start the app: `python app.py`
6. Open `http://127.0.0.1:5000` in your browser.

The SQLite database `study_planner.db` is created automatically on first run, with sample subjects and tasks.

## Features
- Dashboard counts and completion percentage
- Add tasks with subject, deadline and priority
- Mark tasks pending/completed
- Edit and delete tasks
- Search tasks
- Subject progress and simple pending-task summary
- JSON API at `/api/tasks`

Note: Weak-topic detection is a basic pending-task count, not an AI prediction. The calendar is a visual current-month calendar and does not yet show task markers. This is a learning/demo project; add authentication, CSRF protection, and production settings before public deployment.
