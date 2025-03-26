import frappe
from frappe.utils import today

def execute(filters=None):
    """Fetches delayed tasks where end_date has passed but status is NOT Completed"""

    # Ensure filters is not None
    filters = frappe._dict(filters or {})

    # Base conditions and values list
    conditions = ["t.end_date < %s", "t.status != 'Completed'"]
    values = [today()]

    # Apply dynamic filters
    if filters.get("project"):
        conditions.append("t.project = %s")
        values.append(filters["project"])

    if filters.get("assigned_to"):
        conditions.append("t.assigned_to = %s")
        values.append(filters["assigned_to"])

    if filters.get("overdue_days"):
        conditions.append("DATEDIFF(%s, t.end_date) >= %s")
        values.extend([today(), filters["overdue_days"]])

    # Convert conditions list into a valid SQL WHERE clause
    where_clause = " AND ".join(conditions)

    # Fetch overdue tasks
    overdue_tasks = frappe.db.sql("""
        SELECT 
            t.task_name,
            t.project,
            t.assigned_to,
            t.end_date,
            DATEDIFF(%s, t.end_date) AS days_overdue
        FROM `tabTask` t
        WHERE {where_clause}
        ORDER BY days_overdue DESC
    """.format(where_clause=where_clause), tuple(values), as_dict=True)

    # Fetch aggregated data for the chart
    chart_data = frappe.db.sql("""
        SELECT 
            t.project,
            COUNT(*) AS task_count
        FROM `tabTask` t
        WHERE {where_clause}
        GROUP BY t.project
        ORDER BY task_count DESC
    """.format(where_clause=where_clause), tuple(values), as_dict=True)

    # Define table columns
    columns = [
        {"label": "Task Name", "fieldname": "task_name", "fieldtype": "Data", "width": 250},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 150},
        {"label": "Assigned To", "fieldname": "assigned_to", "fieldtype": "Link", "options": "User", "width": 150},
        {"label": "Due Date", "fieldname": "end_date", "fieldtype": "Date", "width": 120},
        {"label": "Days Overdue", "fieldname": "days_overdue", "fieldtype": "Int", "width": 120}
    ]

    # Format chart data for Frappe
    chart = {
        "data": {
            "labels": [d["project"] for d in chart_data],
            "datasets": [{"values": [d["task_count"] for d in chart_data]}]
        },
        "type": "bar",
        "title": "Overdue Tasks by Project"
    }

    return columns, overdue_tasks, None, chart
