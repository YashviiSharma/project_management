import frappe
from frappe.utils import today, add_days

def execute(filters=None):
    """Fetches recent project progress with completed tasks and project updates."""

    start_date = add_days(today(), -7)  # Fetch last 7 days' data

    frappe.msgprint(f"🔹 DEBUG: Fetching data from {start_date}")

    # Fetch All Tasks (Completed, Pending, and Cancelled)
    all_tasks = frappe.db.sql("""
        SELECT t.task_name, t.project, t.assigned_to, t.start_date, t.end_date, t.status, t.creation, t.modified
        FROM `tabTask` t
        WHERE t.modified >= %s
        ORDER BY t.modified DESC
    """, (start_date,), as_dict=True)

    # Fetch Project Progress Updates
    project_updates = frappe.db.sql("""
        SELECT p.name AS project_id, p.project_name, p.progress, p.modified
        FROM `tabProject` p
        WHERE p.modified >= %s
        ORDER BY p.modified DESC
    """, (start_date,), as_dict=True)

    # Debugging: Check if project_updates has data
    frappe.msgprint(f"🔹 DEBUG: Project Updates: {project_updates}")

    if not all_tasks and not project_updates:
        frappe.msgprint("⚠️ No recent data found in the last 7 days.")
        return [], [], [], {}

    # Add Status Symbols for Tasks
    for task in all_tasks:
        if task["status"] == "Completed":
            task["status"] = "🟢 Completed"
        elif task["status"] == "Cancelled":
            task["status"] = "🔴 Cancelled"
        else:
            task["status"] = "🟡 Pending"

    # Table Columns
    columns = [
        {"label": "Task Name", "fieldname": "task_name", "fieldtype": "Data", "width": 250},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
        {"label": "Assigned To", "fieldname": "assigned_to", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 120},
        {"label": "End Date", "fieldname": "end_date", "fieldtype": "Date", "width": 120},
        {"label": "Status", "fieldname": "status", "fieldtype": "Data", "width": 120},
    ]

    # Ensure project_updates contains data before using it
    if project_updates:
        labels = [p["project_name"] for p in project_updates]  # Project names for labels
        values = [p["progress"] for p in project_updates]  # Progress percentage
    else:
        labels, values = [], []  # Avoid errors if no data is available

    # Project Progress Bar Chart with Narrower Bars
    progress_chart = {
        "data": {
            "labels": labels,  # Project names as labels
            "datasets": [
                {
                    "name": "Progress (%)",
                    "values": values,
                    "chartType": "bar",  # Bar Chart
                    "color": "#36A2EB"  # Blue bars
                }
            ],
        },
        "type": "bar",  # Bar chart
        "title": "Project Progress Overview",
        "height": 300,  # Adjust height as needed
        "barOptions": {
            "spaceRatio": 0.8  # Adjusts bar width (Lower value = narrower bars)
        }
    }

    return columns, all_tasks, None, progress_chart  # Now returns Bar Chart with Narrower Bars

