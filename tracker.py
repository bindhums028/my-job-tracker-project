from file_handler import load_applications, save_applications, log_activity
from datetime import date

def get_next_id(applications):
    if not applications:
        return 1
    return max(app["id"] for app in applications) + 1

def add_application(company, role, applied_date, status, notes="", priority="Normal"):
    applications = load_applications()
    new_app = {
        "id": get_next_id(applications),
        "company": company,
        "role": role,
        "date_applied": applied_date,
        "status": status,
        "notes": notes,
        "priority": priority,
        "deadline": "",
        "salary": "",
        "location": ""
    }
    applications.append(new_app)
    save_applications(applications)
    log_activity("Added", f"{role} at {company}")
    return new_app

def get_all_applications():
    return load_applications()

def update_application(app_id, **kwargs):
    applications = load_applications()
    for app in applications:
        if app["id"] == app_id:
            for key, value in kwargs.items():
                if value is not None:
                    app[key] = value
            save_applications(applications)
            log_activity("Updated", f"{app['role']} at {app['company']} → {app.get('status','')}")
            return app
    return None

def delete_application(app_id):
    applications = load_applications()
    target = next((a for a in applications if a["id"] == app_id), None)
    new_list = [a for a in applications if a["id"] != app_id]
    if len(new_list) == len(applications):
        return False
    save_applications(new_list)
    if target:
        log_activity("Deleted", f"{target['role']} at {target['company']}")
    return True

def search_applications(keyword="", status_filter="All", priority_filter="All", sort_by="date_applied"):
    applications = load_applications()
    results = []
    for app in applications:
        keyword_match = (
            not keyword or
            keyword.lower() in app["company"].lower() or
            keyword.lower() in app["role"].lower() or
            keyword.lower() in app.get("notes", "").lower() or
            keyword.lower() in app.get("location", "").lower()
        )
        status_match  = (status_filter == "All"   or app["status"] == status_filter)
        priority_match= (priority_filter == "All" or app.get("priority","Normal") == priority_filter)
        if keyword_match and status_match and priority_match:
            results.append(app)

    # Sorting
    reverse = sort_by in ("id",)
    if sort_by == "company":
        results.sort(key=lambda x: x["company"].lower())
    elif sort_by == "status":
        order = {"Applied": 0, "Interview": 1, "Offer": 2, "Rejected": 3}
        results.sort(key=lambda x: order.get(x["status"], 9))
    elif sort_by == "priority":
        order = {"High": 0, "Normal": 1, "Low": 2}
        results.sort(key=lambda x: order.get(x.get("priority","Normal"), 1))
    else:
        results.sort(key=lambda x: x.get("date_applied",""), reverse=True)
    return results

def get_summary():
    applications = load_applications()
    summary = {"Total": len(applications), "Applied": 0, "Interview": 0, "Offer": 0, "Rejected": 0}
    for app in applications:
        s = app.get("status", "Applied")
        if s in summary:
            summary[s] += 1
    return summary

def get_streak_and_stats():
    applications = load_applications()
    from datetime import datetime, timedelta
    if not applications:
        return {"this_week": 0, "this_month": 0, "success_rate": 0, "top_company": "—"}
    today = date.today()
    week_start  = today - timedelta(days=today.weekday())
    month_start = today.replace(day=1)
    this_week  = sum(1 for a in applications if a.get("date_applied","") >= str(week_start))
    this_month = sum(1 for a in applications if a.get("date_applied","") >= str(month_start))
    offers     = sum(1 for a in applications if a["status"] == "Offer")
    total      = len(applications)
    success    = round((offers / total) * 100) if total else 0
    from collections import Counter
    companies  = Counter(a["company"] for a in applications)
    top        = companies.most_common(1)[0][0] if companies else "—"
    return {"this_week": this_week, "this_month": this_month, "success_rate": success, "top_company": top}
