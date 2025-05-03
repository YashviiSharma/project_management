# Copyright (c) 2025, Aman and Yashvi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, flt, cint, today, add_days, time_diff_in_hours, format_datetime

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_report_summary(data)

    return columns, data, None, chart, summary

def get_columns():
    return [
        {"fieldname": "task_name", "label": "Task Name", "fieldtype": "Data", "width": 200},
        {"fieldname": "project", "label": "Project", "fieldtype": "Link", "options": "Project", "width": 120},
        {"fieldname": "deliverable", "label": "Deliverable", "fieldtype": "Link", "options": "Deliverable", "width": 120},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
        {"fieldname": "priority", "label": "Priority", "fieldtype": "Data", "width": 80},
        {"fieldname": "assigned_to", "label": "Assigned To", "fieldtype": "Link", "options": "User", "width": 120},
        {"fieldname": "start_date", "label": "Start Date", "fieldtype": "Date", "width": 100},
        {"fieldname": "end_date", "label": "Due Date", "fieldtype": "Date", "width": 100},
        {"fieldname": "days_left", "label": "Days Left", "fieldtype": "Int", "width": 80},
        {"fieldname": "progress_", "label": "Progress %", "fieldtype": "Percent", "width": 100},
        {"fieldname": "actual_time", "label": "Time (Mins)", "fieldtype": "Float", "width": 100},
        {"fieldname": "time_logs_count", "label": "Time Logs", "fieldtype": "Int", "width": 80},
        {"fieldname": "actual_start", "label": "Actual Start", "fieldtype": "Datetime", "width": 150},
        {"fieldname": "actual_end", "label": "Actual End", "fieldtype": "Datetime", "width": 150}
    ]

def get_data(filters):
    conditions = get_conditions(filters)

    # Fetch all tasks matching the conditions
    tasks = frappe.get_all(
        "Task",
        filters=conditions,
        fields=[
            "name", "task_name", "project", "status", "priority",
            "assigned_to", "start_date", "end_date", "progress_", 
            "time_in_minutes as actual_time", "actual_start_date", "actual_end_date"
        ],
        order_by="end_date asc, priority desc"
    )

    data = []
    today_date = getdate(today())

    for t in tasks:
        # Calculate days left or overdue
        if t.end_date:
            due_date = getdate(t.end_date)
            t.days_left = (due_date - today_date).days
        else:
            t.days_left = None
        
        # Get time logs
        time_logs = get_task_time_logs(t.name)
        t.time_logs_count = len(time_logs)
        
        # If progress is not set, calculate from time logs
        if not t.progress_ and t.time_logs_count > 0:
            total_progress = sum(log.completed__of_task for log in time_logs if log.completed__of_task)
            t.progress_ = total_progress / t.time_logs_count if t.time_logs_count else 0
        
        # Find associated deliverable (if any)
        t.deliverable = get_related_deliverable(t.name)
        
        # Format datetime fields properly 
        t.actual_start = t.actual_start_date
        t.actual_end = t.actual_end_date
        
        # Remove ID field as we've already extracted necessary values
        del t["name"]
        
        data.append(t)

    return data

def get_conditions(filters):
    conditions = {}

    if filters:
        if filters.get("project"):
            conditions["project"] = filters.get("project")
            
        if filters.get("status"):
            conditions["status"] = filters.get("status")
            
        if filters.get("priority"):
            conditions["priority"] = filters.get("priority")
            
        if filters.get("assigned_to"):
            conditions["assigned_to"] = filters.get("assigned_to")
            
        if filters.get("from_date") and filters.get("to_date"):
            conditions["start_date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
        elif filters.get("from_date"):
            conditions["start_date"] = [">=", filters.get("from_date")]
        elif filters.get("to_date"):
            conditions["end_date"] = ["<=", filters.get("to_date")]
            
        # Handle "Show Overdue" filter properly to show all tasks whose end date
        # is before today but not yet completed
        if cint(filters.get("overdue")):
            conditions["end_date"] = ["<", today()]
            conditions["status"] = ["not in", ["Completed", "Cancelled"]]

    return conditions

def get_task_time_logs(task_id):
    return frappe.get_all(
        "Task Time Log",
        filters={"parent": task_id},
        fields=["member", "from_time", "to_time", "time_in_mins", "completed__of_task"]
    )

def get_related_deliverable(task_id):
    # Find if this task is linked to a deliverable
    # This assumes there's a Deliverable Task child table in Deliverable doctype
    deliverable_task = frappe.db.get_value(
        "Deliverable Task",
        {"task": task_id},
        "parent"
    )

    return deliverable_task

def get_chart_data(data):
    if not data:
        return None

    status_map = {
        "Planned": 0,
        "In Progress": 0,
        "On Hold": 0,
        "Paused": 0,
        "Completed": 0,
        "Cancelled": 0
    }

    for t in data:
        if t.status in status_map:
            status_map[t.status] += 1
        else:
            # Add any status not in our predefined list to "Planned" category
            status_map["Planned"] += 1

    chart = {
        "data": {
            "labels": list(status_map.keys()),
            "datasets": [{"name": "Status Count", "values": list(status_map.values())}]
        },
        "type": "pie",
        "height": 280,
        "colors": ["#8e44ad", "#5e64ff", "#ffa00a", "#ff5858", "#28a745", "#dc3545"]
    }

    return chart

def get_report_summary(data):
    if not data:
        return []

    total_tasks = len(data)
    # Count overdue tasks correctly - end date before today and not completed/cancelled
    overdue = sum(1 for t in data if t.end_date and getdate(t.end_date) < getdate(today()) 
                  and t.status not in ["Completed", "Cancelled"])

    status_counts = {
        "Planned": sum(1 for t in data if t.status == "Planned"),
        "In Progress": sum(1 for t in data if t.status == "In Progress"),
        "On Hold": sum(1 for t in data if t.status == "On Hold"),
        "Paused": sum(1 for t in data if t.status == "Paused"),
        "Completed": sum(1 for t in data if t.status == "Completed"),
        "Cancelled": sum(1 for t in data if t.status == "Cancelled")
    }

    # Calculate total time spent
    total_time_mins = sum(t.actual_time or 0 for t in data)
    total_time_hours = total_time_mins / 60

    # Calculate average progress across all tasks
    total_progress = sum(t.progress_ or 0 for t in data)
    avg_progress = total_progress / total_tasks if total_tasks else 0

    # Priority breakdown
    priority_counts = {
        "Critical": sum(1 for t in data if t.priority == "Critical"),
        "High": sum(1 for t in data if t.priority == "High"),
        "Medium": sum(1 for t in data if t.priority == "Medium"),
        "Low": sum(1 for t in data if t.priority == "Low")
    }

    return [
        {"label": "Total Tasks", "value": total_tasks, "indicator": "blue"},
        {"label": "Overdue", "value": overdue, "indicator": "red"},
        {"label": "Completed", "value": status_counts["Completed"], "indicator": "green"},
        {"label": "In Progress", "value": status_counts["In Progress"], "indicator": "orange"},
        {"label": "Total Hours", "value": f"{total_time_hours:.1f}", "indicator": "purple"},
        {"label": "Avg. Progress", "value": f"{avg_progress:.1f}%", "indicator": "blue"}
    ]