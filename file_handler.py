import json
import os
import hashlib

USERS_FILE     = "users.json"
ACTIVITY_FILE  = "activity.json"

# ── Current logged-in user (set at login) ──────────────────────
_current_user = None

def set_current_user(username):
    global _current_user
    _current_user = username

def get_current_user():
    return _current_user

def get_user_applications_file():
    """Each user gets their own applications file: applications_bindhu MS.json"""
    if _current_user:
        safe_name = _current_user.replace(" ", "_").replace("/", "_")
        return f"applications_{safe_name}.json"
    return "applications.json"

def get_user_activity_file():
    """Each user gets their own activity log file"""
    if _current_user:
        safe_name = _current_user.replace(" ", "_").replace("/", "_")
        return f"activity_{safe_name}.json"
    return ACTIVITY_FILE

# ── Hashing ────────────────────────────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ── User management ────────────────────────────────────────────
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Username already exists!"
    users[username] = {
        "password": hash_password(password),
        "created": str(__import__('datetime').date.today())
    }
    save_users(users)
    return True, "Account created successfully!"

def verify_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Username not found!"
    if users[username]["password"] != hash_password(password):
        return False, "Wrong password!"
    return True, "Login successful!"

# ── Applications (per user) ────────────────────────────────────
def load_applications():
    file_name = get_user_applications_file()
    if not os.path.exists(file_name):
        return []
    try:
        with open(file_name, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_applications(applications):
    file_name = get_user_applications_file()
    with open(file_name, "w") as f:
        json.dump(applications, f, indent=4)

# ── Activity log (per user) ────────────────────────────────────
def load_activity():
    file_name = get_user_activity_file()
    if not os.path.exists(file_name):
        return []
    try:
        with open(file_name, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def log_activity(action, detail):
    from datetime import datetime
    activity = load_activity()
    activity.insert(0, {
        "action": action,
        "detail": detail,
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
    })
    activity = activity[:20]
    file_name = get_user_activity_file()
    with open(file_name, "w") as f:
        json.dump(activity, f, indent=4)
