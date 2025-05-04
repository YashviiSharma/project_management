# Copyright (c) 2025, Aman and Yashvi and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils import getdate, flt, today, add_days, time_diff_in_hours, format_datetime

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_report_summary(data)

    return columns, data, None, chart, summary

def get_columns():
    return [
        {"fieldname": "member_name", "label": _("Member"), "fieldtype": "Data", "width": 150},
        {"fieldname": "total_tasks", "label": _("Total Tasks"), "fieldtype": "Int", "width": 100},
        {"fieldname": "completed_tasks", "label": _("Completed Tasks"), "fieldtype": "Int", "width": 120},
        {"fieldname": "in_progress_tasks", "label": _("In Progress Tasks"), "fieldtype": "Int", "width": 150},
        {"fieldname": "total_time_mins", "label": _("Total Time (Mins)"), "fieldtype": "Float", "width": 120},
        {"fieldname": "avg_time_per_task", "label": _("Avg Time/Task (Mins)"), "fieldtype": "Float", "width": 150},
        {"fieldname": "efficiency", "label": _("Efficiency %"), "fieldtype": "Percent", "width": 100},
        {"fieldname": "last_active", "label": _("Last Active"), "fieldtype": "Datetime", "width": 150}
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    time_log_filters = {"member": ["!=", ""]}
    if conditions.get("from_date"):
        time_log_filters["from_time"] = [">=", conditions["from_date"]]
    if conditions.get("to_date"):
        time_log_filters["to_time"] = ["<=", add_days(conditions["to_date"], 1)]
    
    members = frappe.get_all(
        "Task Time Log",
        filters=time_log_filters,
        fields=["DISTINCT member"],
        group_by="member"
    )
    
    data = []
    
    for member in members:
        member_data = get_member_data(member.member, conditions)
        if member_data:
            data.append(member_data)
    
    data.sort(key=lambda x: x['total_time_mins'], reverse=True)
    
    return data

def get_member_data(member, conditions):
    # Get member name from User document
    member_name = frappe.db.get_value("User", member, "full_name") or member
    
    task_filters = {"assigned_to": member}
    if conditions.get("project"):
        task_filters["project"] = conditions["project"]
    
    assigned_tasks = frappe.get_all(
        "Task",
        filters=task_filters,
        fields=["name", "status", "time_in_minutes"]
    )
    
    time_log_filters = {"member": member}
    if conditions.get("from_date"):
        time_log_filters["from_time"] = [">=", conditions["from_date"]]
    if conditions.get("to_date"):
        time_log_filters["to_time"] = ["<=", add_days(conditions["to_date"], 1)]
    
    time_logs = frappe.get_all(
        "Task Time Log",
        filters=time_log_filters,
        fields=["from_time", "to_time", "time_in_mins", "completed__of_task", "parent"]
    )
    
    total_tasks = len(assigned_tasks)
    # Any task not marked as "Completed" is considered "In Progress"
    completed_tasks = len([t for t in assigned_tasks if t.status == "Completed"])
    in_progress_tasks = total_tasks - completed_tasks
    
    total_time_mins = sum(log.time_in_mins for log in time_logs if log.time_in_mins)
    
    avg_time_per_task = flt(total_time_mins) / len(time_logs) if time_logs else 0
    
    efficiency = 0
    if total_tasks > 0:
        efficiency = (completed_tasks / total_tasks) * 100
    
    last_active = max(log.to_time for log in time_logs if log.to_time) if time_logs else None
    
    return {
        "member": member,  # Keep the original member ID for reference
        "member_name": member_name,  # Add member name for display
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "in_progress_tasks": in_progress_tasks,
        "total_time_mins": total_time_mins,
        "avg_time_per_task": avg_time_per_task,
        "efficiency": efficiency,
        "last_active": last_active
    }

def get_conditions(filters):
    conditions = {}
    
    if filters:
        if filters.get("from_date"):
            conditions["from_date"] = filters.get("from_date")
        if filters.get("to_date"):
            conditions["to_date"] = filters.get("to_date")
        if filters.get("project"):
            conditions["project"] = filters.get("project")
    
    return conditions

def get_chart_data(data):
    if not data:
        return None
    
    chart = {
        "data": {
            "labels": [d["member_name"] for d in data],  # Use member name instead of ID
            "datasets": [
                {
                    "name": "Total Time (Hours)",  # Display in hours for chart
                    "values": [round(d["total_time_mins"] / 60, 2) for d in data],  # Convert minutes to hours
                    "chartType": "bar"
                },
                {
                    "name": "Completed Tasks",
                    "values": [d["completed_tasks"] for d in data],
                    "chartType": "line"
                },
                {
                    "name": "In Progress Tasks",
                    "values": [d["in_progress_tasks"] for d in data],
                    "chartType": "line"
                }
            ]
        },
        "type": "axis-mixed",
        "height": 300,
        "colors": ["#5e64ff", "#28a745", "#ffc107"],
        "title": "Time Spent vs Task Status",
        "barOptions": {
            "spaceRatio": 0.5
        },
        "axisOptions": {
            "xAxisMode": "tick",
            "yAxisMode": "tick"
        }
    }
    
    return chart

def get_report_summary(data):
    if not data:
        return []
    
    total_members = len(data)
    total_time_mins = sum(d["total_time_mins"] for d in data)
    avg_time_per_member = total_time_mins / total_members if total_members else 0
    total_tasks = sum(d["total_tasks"] for d in data)
    total_completed = sum(d["completed_tasks"] for d in data)
    total_in_progress = sum(d["in_progress_tasks"] for d in data)
    avg_efficiency = sum(d["efficiency"] for d in data) / total_members if total_members else 0
    
    return [
        {"label": "Total Members", "value": total_members, "indicator": "blue"},
        {"label": "Total Time (Mins)", "value": f"{total_time_mins:.0f}", "indicator": "green"},
        {"label": "Avg Time/Member", "value": f"{avg_time_per_member:.0f} mins", "indicator": "purple"},
        {"label": "Total Tasks", "value": total_tasks, "indicator": "orange"},
        {"label": "Completed Tasks", "value": total_completed, "indicator": "green"},
        {"label": "In Progress Tasks", "value": total_in_progress, "indicator": "yellow"},
        {"label": "Avg Efficiency", "value": f"{avg_efficiency:.1f}%", "indicator": "blue"}
    ]