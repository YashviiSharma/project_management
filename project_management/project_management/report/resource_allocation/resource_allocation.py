# Copyright (c) 2025, Aman and Yashvi and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    
    chart = get_chart_data(data) if data else None
    
    return columns, data, None, chart

def get_columns():
    columns = [
        {
            "label": _("Team Member"),
            "fieldname": "team_member",
            "fieldtype": "Link",
            "options": "User",
            "width": 150
        },
        {
            "label": _("Full Name"),
            "fieldname": "full_name",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Project"),
            "fieldname": "project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 150
        },
        {
            "label": _("Project Name"),
            "fieldname": "project_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Task"),
            "fieldname": "task",
            "fieldtype": "Link",
            "options": "Task",
            "width": 150
        },
        {
            "label": _("Task Name"),
            "fieldname": "task_name",
            "fieldtype": "Data",
            "width": 200
        },
        {
            "label": _("Status"),
            "fieldname": "status",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Progress"),
            "fieldname": "progress",
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "label": _("Priority"),
            "fieldname": "priority",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "label": _("Start Date"),
            "fieldname": "start_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("End Date"),
            "fieldname": "end_date",
            "fieldtype": "Date",
            "width": 100
        },
        {
            "label": _("Is Vendor"),
            "fieldname": "is_vendor",
            "fieldtype": "Check",
            "width": 80
        }
    ]
    return columns

def get_data(filters):
    filters = frappe._dict(filters or {})
    data = []
    
    team_members = get_team_members(filters)
    
    for member in team_members:
        projects = get_projects_for_member(member.user, filters)
        
        for project in projects:
            tasks = get_tasks_for_member(member.user, project.name, filters)
            
            if not tasks:
                data.append({
                    "team_member": member.user,
                    "full_name": member.full_name,
                    "is_vendor": member.is_vendor,
                    "project": project.name,
                    "project_name": project.project_name,
                    "task": None,
                    "task_name": None,
                    "status": project.status,
                    "progress": project.progress,
                    "priority": project.priority,
                    "start_date": project.start_date,
                    "end_date": project.end_date
                })
            else:
                # Add a row for each task
                for task in tasks:
                    data.append({
                        "team_member": member.user,
                        "full_name": member.full_name,
                        "is_vendor": member.is_vendor,
                        "project": project.name,
                        "project_name": project.project_name,
                        "task": task.name,
                        "task_name": task.task_name,
                        "status": task.status,
                        "progress": task.progress_,
                        "priority": task.priority,
                        "start_date": task.start_date,
                        "end_date": task.end_date
                    })
    
    return data

def get_team_members(filters):
    """Get all team members based on filters"""
    team_member_filters = {}
    
    if filters.get("team_member"):
        team_member_filters["user"] = filters.get("team_member")
    
    if filters.get("is_vendor"):
        team_member_filters["is_vendor"] = 1
    
    team_members = frappe.db.get_all(
        "Team Member",
        filters=team_member_filters,
        fields=["distinct user", "full_name", "is_vendor"]
    )
    
    return team_members

def get_projects_for_member(user, filters):
    """Get projects where the user is a team member"""
    project_filters = {"docstatus": ["<", 2]}
    
    if filters.get("project"):
        project_filters["name"] = filters.get("project")
    
    if filters.get("status"):
        project_filters["status"] = filters.get("status")
    
    project_names = frappe.db.get_all(
        "Team Member",
        filters={"user": user},
        pluck="parent"
    )
    
    if not project_names:
        return []
    
    project_filters["name"] = ["in", project_names]
    
    projects = frappe.db.get_all(
        "Project",
        filters=project_filters,
        fields=["name", "project_name", "status", "progress", "priority", "start_date", "end_date"]
    )
    
    return projects

def get_tasks_for_member(user, project, filters):
    """Get tasks assigned to this user in this project"""
    task_filters = {
        "docstatus": ["<", 2],
        "assigned_to": user,
        "project": project
    }
    
    if filters.get("status"):
        task_filters["status"] = filters.get("status")
    
    if filters.get("priority"):
        task_filters["priority"] = filters.get("priority")
    
    tasks = frappe.db.get_all(
        "Task",
        filters=task_filters,
        fields=["name", "task_name", "status", "progress_", "priority", "start_date", "end_date"]
    )
    
    return tasks

def get_chart_data(data):
    if not data:
        return None
    
    status_count = {}
    member_project_count = {}
    priority_count = {}
    
    for row in data:
        if row.get("status"):
            status_count[row["status"]] = status_count.get(row["status"], 0) + 1
        
        if row.get("team_member") and row.get("project"):
            if row["team_member"] not in member_project_count:
                member_project_count[row["team_member"]] = set()
            member_project_count[row["team_member"]].add(row["project"])
        
        if row.get("priority"):
            priority_count[row["priority"]] = priority_count.get(row["priority"], 0) + 1
    
    datasets = []
    
    if status_count:
        datasets.append({
            "name": "By Status",
            "values": list(status_count.values()),
            "chartType": "bar"
        })
    
    if priority_count:
        datasets.append({
            "name": "By Priority",
            "values": list(priority_count.values()),
            "chartType": "bar"
        })
    
    if not datasets:
        return None
    
    chart = {
        "data": {
            "labels": list(status_count.keys()) if status_count else list(priority_count.keys()),
            "datasets": datasets
        },
        "type": "axis-mixed",
        "height": 300,
        "colors": ["#7CD6FD", "#743EE2", "#FF5858"],
        "barOptions": {
            "spaceRatio": 0.2
        },
        "axisOptions": {
            "xIsSeries": True
        }
    }
    
    return chart