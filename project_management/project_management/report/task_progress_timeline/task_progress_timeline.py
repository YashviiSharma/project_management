# Copyright (c) 2025, Aman and Yashvi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import today, add_days, getdate, get_datetime, date_diff, now_datetime
from frappe.query_builder.functions import Count, Sum, Avg
from datetime import datetime, timedelta
import json

def execute(filters=None):
    if not filters:
        filters = {}
    
    if not filters.get("time_interval"):
        filters["time_interval"] = "this_week"
    
    date_range = get_date_range(filters)
    filters["from_date"] = date_range["from_date"]
    filters["to_date"] = date_range["to_date"]
    
    data = get_report_data(filters)
    columns = get_columns(filters)
    chart = get_task_status_chart(data)
    summary = get_report_summary(data, filters)
    
    return columns, data, None, chart, summary

def get_date_range(filters):
    today_date = getdate(today())
    
    if filters.get("from_date") and filters.get("to_date"):
        return {
            "from_date": filters.get("from_date"),
            "to_date": filters.get("to_date")
        }
    
    time_interval = filters.get("time_interval")
    
    if time_interval == "today":
        return {
            "from_date": today_date,
            "to_date": today_date
        }
    elif time_interval == "yesterday":
        yesterday = add_days(today_date, -1)
        return {
            "from_date": yesterday,
            "to_date": yesterday
        }
    elif time_interval == "this_week":
        this_week_start = add_days(today_date, -today_date.weekday())
        this_week_end = add_days(this_week_start, 6)
        return {
            "from_date": this_week_start,
            "to_date": this_week_end if this_week_end <= today_date else today_date
        }
    elif time_interval == "last_week":
        last_week_start = add_days(today_date, -today_date.weekday() - 7)
        last_week_end = add_days(last_week_start, 6)
        return {
            "from_date": last_week_start,
            "to_date": last_week_end
        }
    elif time_interval == "this_month":
        month_start = today_date.replace(day=1)
        return {
            "from_date": month_start,
            "to_date": today_date
        }
    elif time_interval == "last_month":
        current_month_start = today_date.replace(day=1)
        last_month_end = add_days(current_month_start, -1)
        last_month_start = last_month_end.replace(day=1)
        return {
            "from_date": last_month_start,
            "to_date": last_month_end
        }
    elif time_interval == "this_quarter":
        quarter = (today_date.month - 1) // 3 + 1
        quarter_start_month = (quarter - 1) * 3 + 1
        quarter_start = today_date.replace(month=quarter_start_month, day=1)
        return {
            "from_date": quarter_start,
            "to_date": today_date
        }
    elif time_interval == "last_quarter":
        current_quarter = (today_date.month - 1) // 3 + 1
        last_quarter = current_quarter - 1 if current_quarter > 1 else 4
        last_quarter_year = today_date.year if current_quarter > 1 else today_date.year - 1
        last_quarter_start_month = (last_quarter - 1) * 3 + 1
        last_quarter_start = datetime(last_quarter_year, last_quarter_start_month, 1).date()
        last_quarter_end_month = last_quarter * 3
        if last_quarter_end_month == 12:
            last_quarter_end = datetime(last_quarter_year, 12, 31).date()
        else:
            last_quarter_end = datetime(last_quarter_year, last_quarter_end_month + 1, 1).date()
            last_quarter_end = add_days(last_quarter_end, -1)
        return {
            "from_date": last_quarter_start,
            "to_date": last_quarter_end
        }
    elif time_interval == "this_year":
        year_start = today_date.replace(month=1, day=1)
        return {
            "from_date": year_start,
            "to_date": today_date
        }
    elif time_interval == "last_year":
        last_year_start = datetime(today_date.year - 1, 1, 1).date()
        last_year_end = datetime(today_date.year - 1, 12, 31).date()
        return {
            "from_date": last_year_start,
            "to_date": last_year_end
        }
    elif time_interval == "all":
        return {
            "from_date": datetime(2000, 1, 1).date(),
            "to_date": today_date
        }
    else:
        return {
            "from_date": frappe.datetime.week_start(),
            "to_date": frappe.datetime.week_end()
        }

def get_report_data(filters):
    task_filters = []
    
    if filters.get("project"):
        task_filters.append(["project", "=", filters.get("project")])
    
    if filters.get("status"):
        task_filters.append(["status", "=", filters.get("status")])
    
    if filters.get("priority"):
        task_filters.append(["priority", "=", filters.get("priority")])
    
    if filters.get("assigned_to"):
        task_filters.append(["_assign", "like", f'%"{filters.get("assigned_to")}"%'])
    
    # Time based filters for tasks
    if filters.get("filter_based_on") == "modified":
        task_filters.append(["modified", "between", [filters.get("from_date"), filters.get("to_date")]])
    elif filters.get("filter_based_on") == "creation":
        task_filters.append(["creation", "between", [filters.get("from_date"), filters.get("to_date")]])
    elif filters.get("filter_based_on") == "start_date":
        task_filters.append(["start_date", "between", [filters.get("from_date"), filters.get("to_date")]])
    elif filters.get("filter_based_on") == "end_date":
        task_filters.append(["end_date", "between", [filters.get("from_date"), filters.get("to_date")]])
    else:
        task_filters.append(["modified", "between", [filters.get("from_date"), filters.get("to_date")]])
    
    # Get all tasks matching the filters
    all_tasks = frappe.get_all(
        "Task",
        filters=task_filters,
        fields=[
            "name", "task_name", "project", "assigned_to", "_assign", 
            "start_date", "end_date", "status", "priority", "progress_",
            "creation", "modified", "time_in_minutes"
        ],
        order_by="modified desc"
    )
    
    # Mark backlog tasks if show_backlogs is enabled
    if filters.get("show_backlogs"):
        backlog_tasks = frappe.get_all(
            "Task",
            filters=[
                ["end_date", "<", today()],
                ["status", "not in", ["Completed", "Cancelled"]]
            ],
            fields=["name"],
            pluck="name"
        )
        
        backlog_set = set(backlog_tasks)
        for task in all_tasks:
            task["is_backlog"] = 1 if task["name"] in backlog_set else 0
    else:
        for task in all_tasks:
            task["is_backlog"] = 0
    
    today_date = getdate(today())
    
    for task in all_tasks:
        if task["status"] == "Completed":
            task["status_display"] = "🟢 Completed"
        elif task["status"] == "Cancelled":
            task["status_display"] = "⚫ Cancelled"
        elif task["status"] == "In Progress":
            task["status_display"] = "🟡 In Progress"
        elif task["status"] == "On Hold" or task["status"] == "Paused":
            task["status_display"] = "🟠 On Hold"
        elif task["is_backlog"]:
            task["status_display"] = "🔴 Backlog"
        else:
            task["status_display"] = "⚪ " + task["status"]
        
        if task["end_date"]:
            days_left = date_diff(task["end_date"], today_date)
            if days_left < 0:
                task["days_left"] = f"🔴 {abs(days_left)} days overdue"
            elif days_left == 0:
                task["days_left"] = "⚠️ Due today"
            else:
                task["days_left"] = f"🟢 {days_left} days left"
        else:
            task["days_left"] = ""
        
        task["deliverable"] = get_deliverable_for_task(task["name"])
        
        assigned_users = []
        if task["_assign"]:
            try:
                assigned_data = json.loads(task["_assign"])
                for user_id in assigned_data:
                    user_name = get_user_name(user_id)
                    assigned_users.append(user_name)
            except:
                pass
        
        if not assigned_users and task["assigned_to"]:
            user_name = get_user_name(task["assigned_to"])
            assigned_users.append(user_name)
        
        task["assigned_users"] = ", ".join(assigned_users) if assigned_users else ""
        
        if task["time_in_minutes"]:
            hours = int(task["time_in_minutes"] // 60)
            minutes = int(task["time_in_minutes"] % 60)
            task["time_spent"] = f"{hours}h {minutes}m"
        else:
            task["time_spent"] = ""
    
    project_filters = []
    
    if filters.get("project"):
        project_filters.append(["name", "=", filters.get("project")])
    
    projects = frappe.get_all(
        "Project",
        filters=project_filters,
        fields=[
            "name", "project_name", "status", "priority", 
            "start_date", "end_date", "progress", "modified"
        ],
        order_by="modified desc"
    )
    
    project_map = {p.name: p for p in projects}
    
    for task in all_tasks:
        if task["project"] in project_map:
            project = project_map[task["project"]]
            task["project_name"] = project.project_name
            task["project_status"] = project.status
            task["project_progress"] = project.progress
        else:
            task["project_name"] = task["project"]
            task["project_status"] = ""
            task["project_progress"] = 0
    
    return all_tasks

def get_deliverable_for_task(task_id):
    deliverable_task = frappe.get_all(
        "Deliverable Task",
        filters={"task": task_id},
        fields=["parent"],
        limit=1
    )
    
    if deliverable_task:
        deliverable = frappe.get_all(
            "Deliverable",
            filters={"name": deliverable_task[0].parent},
            fields=["name", "deliverable_name", "status"],
            limit=1
        )
        
        if deliverable:
            return f"{deliverable[0].deliverable_name} ({deliverable[0].status})"
    
    return ""

def get_user_name(user_id):
    if not user_id:
        return ""
    
    user_name = frappe.cache().hget("user_fullname", user_id)
    
    if not user_name:
        user = frappe.get_all(
            "User",
            filters={"name": user_id},
            fields=["full_name"],
            limit=1
        )
        
        if user:
            user_name = user[0].full_name
            frappe.cache().hset("user_fullname", user_id, user_name)
        else:
            user_name = user_id
    
    return user_name

def get_columns(filters):
    return [
        {"label": "Task", "fieldname": "task_name", "fieldtype": "Data", "width": 200},
        {"label": "Project", "fieldname": "project", "fieldtype": "Link", "options": "Project", "width": 120},
        {"label": "Deliverable", "fieldname": "deliverable", "fieldtype": "Data", "width": 180},
        {"label": "Status", "fieldname": "status_display", "fieldtype": "Data", "width": 120},
        {"label": "Priority", "fieldname": "priority", "fieldtype": "Data", "width": 80},
        {"label": "Assigned To", "fieldname": "assigned_users", "fieldtype": "Data", "width": 150},
        {"label": "Progress", "fieldname": "progress_", "fieldtype": "Percent", "width": 100},
        {"label": "Timeline", "fieldname": "days_left", "fieldtype": "Data", "width": 130},
        {"label": "Start Date", "fieldname": "start_date", "fieldtype": "Date", "width": 100},
        {"label": "Due Date", "fieldname": "end_date", "fieldtype": "Date", "width": 100},
        {"label": "Time Spent", "fieldname": "time_spent", "fieldtype": "Data", "width": 100},
        {"label": "Last Modified", "fieldname": "modified", "fieldtype": "Datetime", "width": 150},
    ]

def get_task_status_chart(data):
    if not data:
        return None
    
    status_counts = {}
    for task in data:
        status = task["status"]
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    
    return {
        "data": {
            "labels": list(status_counts.keys()),
            "datasets": [{"name": "Task Status", "values": list(status_counts.values())}]
        },
        "type": "pie",
        "height": 300,  
        "colors": ["#4caf50", "#ff5722", "#2196f3", "#ff9800", "#9c27b0", "#607d8b"],
        "title": "Task Status Distribution"
    }

def get_report_summary(data, filters):
    if not data:
        return []
    
    total_tasks = len(data)
    completed_tasks = sum(1 for task in data if task["status"] == "Completed")
    in_progress_tasks = sum(1 for task in data if task["status"] == "In Progress")
    backlog_tasks = sum(1 for task in data if task["is_backlog"])
    
    total_minutes = sum(task["time_in_minutes"] or 0 for task in data)
    total_hours = total_minutes / 60
    
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    progress_values = [task["progress_"] for task in data if task["progress_"] is not None]
    avg_progress = sum(progress_values) / len(progress_values) if progress_values else 0
    
    date_range = f"{filters.get('from_date')} to {filters.get('to_date')}"
    
    return [
        {"label": "Time Period", "value": date_range, "indicator": "blue"},
        {"label": "Total Tasks", "value": total_tasks, "indicator": "blue"},
        {"label": "Completed", "value": completed_tasks, "indicator": "green"},
        {"label": "In Progress", "value": in_progress_tasks, "indicator": "orange"},
        {"label": "Backlog", "value": backlog_tasks, "indicator": "red"},
        {"label": "Completion Rate", "value": f"{completion_rate:.1f}%", "indicator": "green" if completion_rate > 50 else "orange"},
        {"label": "Avg Progress", "value": f"{avg_progress:.1f}%", "indicator": "blue"},
        {"label": "Total Hours", "value": f"{total_hours:.1f}h", "indicator": "purple"}
    ]