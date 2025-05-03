import frappe
import json

def execute(filters=None):
    users_to_include = get_relevant_users(filters)
    
    user_details = {user_id: get_user_name(user_id) for user_id in users_to_include}
    
    user_data = {
        user_id: {
            "full_name": user_details.get(user_id, user_id),
            "total_tasks": 0,
            "completed_tasks": 0,
            "in_progress_tasks": 0,
            "planned_tasks": 0,
            "on_hold_tasks": 0,
            "total_time_minutes": 0,
            "completion_percentage": 0,
            "high_priority_tasks": 0,
            "time_spent": "0h 0m",
            "recent_tasks": ""
        } for user_id in users_to_include
    }
    
    task_filters = build_task_filters(filters)
    
    process_all_tasks(user_data, filters.get('project') if filters else None)
    
    add_recent_tasks(user_data, filters.get('project') if filters else None)
    
    data = prepare_final_data(user_data)
    
    columns = get_columns()
    
    chart = prepare_chart(data)
    
    report_summary = generate_summary(data, len(users_to_include))
    
    return columns, data, None, chart, report_summary

def get_relevant_users(filters):
    users = []
    project_filter = filters.get('project') if filters else None
    
    if project_filter:
        task_assignments = frappe.get_all(
            "Task",
            filters={"project": project_filter},
            fields=["assigned_to", "_assign"],
            distinct=True
        )
        
        for task in task_assignments:
            if task.assigned_to and task.assigned_to not in users:
                users.append(task.assigned_to)
                
            if task._assign:
                try:
                    for user in json.loads(task._assign):
                        if user and user not in users:
                            users.append(user)
                except:
                    pass
    else:
        users = [user.name for user in frappe.get_all(
            "User",
            filters={"enabled": 1, "name": ["not in", ["Administrator", "Guest"]]},
            fields=["name"]
        )]
    
    for task in frappe.get_all("Task", filters={"assigned_to": ["is", "set"]}, fields=["assigned_to"], distinct=True):
        if task.assigned_to and task.assigned_to not in users:
            users.append(task.assigned_to)

    for task in frappe.get_all("Task", filters={"_assign": ["is", "set"]}, fields=["_assign"], distinct=True):
        if task._assign:
            try:
                for user in json.loads(task._assign):
                    if user and user not in users:
                        users.append(user)
            except:
                pass
    
    return users

def get_user_name(user_id):
    user_doc = frappe.get_all(
        "User", 
        filters={"name": user_id}, 
        fields=["full_name"], 
        limit=1
    )
    return user_doc[0].full_name if user_doc and user_doc[0].full_name else user_id

def build_task_filters(filters):
    conditions = {}
    if filters:
        for field in ['project', 'status', 'priority']:
            if filters.get(field):
                conditions[field] = filters.get(field)
        
        if filters.get('from_date') and filters.get('to_date'):
            conditions["start_date"] = ["between", [filters.get('from_date'), filters.get('to_date')]]
    
    return conditions

def process_all_tasks(user_data, project_filter=None):
    all_task_conditions = {"project": project_filter} if project_filter else {}
    
    all_tasks = frappe.get_all(
        "Task",
        filters=all_task_conditions,
        fields=["name", "assigned_to", "status", "_assign", "time_in_minutes", "priority"]
    )
    
    task_counters = {user_id: 0 for user_id in user_data}
    
    for task in all_tasks:
        if task.assigned_to and task.assigned_to in user_data:
            update_user_stats(user_data, task, task.assigned_to)
            task_counters[task.assigned_to] += 1
        
        if task._assign:
            try:
                assigned_users = json.loads(task._assign)
                for user_id in assigned_users:
                    if user_id in user_data:
                        update_user_stats(user_data, task, user_id)
                        task_counters[user_id] += 1
            except:
                pass
    
    for user_id, count in task_counters.items():
        user_data[user_id]["total_tasks"] = count

def update_user_stats(user_data, task, user_id):
    if task.status == "Completed":
        user_data[user_id]["completed_tasks"] += 1
    elif task.status == "In Progress":
        user_data[user_id]["in_progress_tasks"] += 1
    elif task.status == "Planned":
        user_data[user_id]["planned_tasks"] += 1
    elif task.status in ["On Hold", "Paused"]:
        user_data[user_id]["on_hold_tasks"] += 1
    
    if hasattr(task, 'priority') and task.priority in ["High", "Critical"]:
        user_data[user_id]["high_priority_tasks"] += 1

    if task.time_in_minutes:
        user_data[user_id]["total_time_minutes"] += float(task.time_in_minutes or 0)

def add_recent_tasks(user_data, project_filter=None):
    for user_id in user_data:
        tasks = []
        
        direct_tasks = frappe.get_all(
            "Task",
            filters={"assigned_to": user_id} if not project_filter else 
                   {"assigned_to": user_id, "project": project_filter},
            fields=["task_name", "modified"],
            order_by="modified desc",
            limit=3
        )
        tasks.extend(direct_tasks)
        
        json_filter = {"_assign": ["like", f"%{user_id}%"]}
        if project_filter:
            json_filter["project"] = project_filter
            
        json_tasks = frappe.get_all(
            "Task",
            filters=json_filter,
            fields=["task_name", "modified", "_assign"],
            order_by="modified desc",
            limit=5
        )
        
        for task in json_tasks:
            try:
                if user_id in json.loads(task._assign):
                    tasks.append(task)
            except:
                pass
        
        tasks.sort(key=lambda x: x.modified, reverse=True)
        tasks = tasks[:3]
        
        user_data[user_id]["recent_tasks"] = ", ".join([task.task_name for task in tasks]) if tasks else ""

def prepare_final_data(user_data):
    data = []
    for user_id, user_info in user_data.items():
        if user_info["total_tasks"] > 0:
            user_info["completion_percentage"] = (user_info["completed_tasks"] / user_info["total_tasks"]) * 100
        
        total_minutes = int(user_info["total_time_minutes"] or 0)
        hours, minutes = divmod(total_minutes, 60)
        user_info["time_spent"] = f"{hours}h {minutes}m"
        
        if user_info["total_tasks"] > 0 or user_info["recent_tasks"]:
            data.append({
                "full_name": user_info["full_name"],
                "total_tasks": user_info["total_tasks"],
                "completed_tasks": user_info["completed_tasks"],
                "in_progress_tasks": user_info["in_progress_tasks"],
                "planned_tasks": user_info["planned_tasks"],
                "on_hold_tasks": user_info["on_hold_tasks"],
                "completion_percentage": user_info["completion_percentage"],
                "high_priority_tasks": user_info["high_priority_tasks"],
                "time_spent": user_info["time_spent"],
                "recent_tasks": user_info["recent_tasks"]
            })
    
    return sorted(data, key=lambda x: x["total_tasks"], reverse=True)

def get_columns():
    return [
        {"fieldname": "full_name", "label": "Team Member", "fieldtype": "Data", "width": 180},
        {"fieldname": "total_tasks", "label": "Total Tasks", "fieldtype": "Int", "width": 100},
        {"fieldname": "completed_tasks", "label": "Completed", "fieldtype": "Int", "width": 100},
        {"fieldname": "in_progress_tasks", "label": "In Progress", "fieldtype": "Int", "width": 100},
        {"fieldname": "planned_tasks", "label": "Planned", "fieldtype": "Int", "width": 100},
        {"fieldname": "on_hold_tasks", "label": "On Hold", "fieldtype": "Int", "width": 100},
        {"fieldname": "completion_percentage", "label": "Completion %", "fieldtype": "Percent", "width": 120},
        {"fieldname": "high_priority_tasks", "label": "High Priority", "fieldtype": "Int", "width": 120},
        {"fieldname": "time_spent", "label": "Time Spent", "fieldtype": "Data", "width": 120},
        {"fieldname": "recent_tasks", "label": "Recent Tasks", "fieldtype": "Data", "width": 200}
    ]

def prepare_chart(data):
    if not data:
        return None
        
    chart_data = data[:10]
    
    users = []
    completed = []
    in_progress = []
    planned = []
    on_hold = []
    
    for row in chart_data:
        if row["total_tasks"] > 0:
            users.append(row["full_name"])
            completed.append(row["completed_tasks"])
            in_progress.append(row["in_progress_tasks"])
            planned.append(row["planned_tasks"])
            on_hold.append(row["on_hold_tasks"])
    
    if not users:
        return None
        
    return {
        "data": {
            "labels": users,
            "datasets": [
                {"name": "Completed", "values": completed},
                {"name": "In Progress", "values": in_progress},
                {"name": "Planned", "values": planned},
                {"name": "On Hold", "values": on_hold}
            ]
        },
        "type": "bar",
        "height": 300,
        "colors": ["#4caf50", "#2196f3", "#ff9800", "#9c27b0"],
        "stacked": 1,
        "title": "Team Member Workload Distribution"
    }

def generate_summary(data, total_team_members):
    active_team_members = len(data)
    total_assigned_tasks = sum(row["total_tasks"] for row in data)
    total_completed_tasks = sum(row["completed_tasks"] for row in data)
    
    overall_completion = (total_completed_tasks / total_assigned_tasks * 100) if total_assigned_tasks > 0 else 0
    
    return [
        {"label": "Total Team Members", "value": total_team_members, "indicator": "blue"},
        {"label": "Active Members", "value": active_team_members, "indicator": "green"},
        {"label": "Total Tasks", "value": total_assigned_tasks, "indicator": "blue"},
        {"label": "Completed Tasks", "value": total_completed_tasks, "indicator": "green"},
        {"label": "Overall Completion", "value": f"{overall_completion:.1f}%", "indicator": "green" if overall_completion > 50 else "orange"}
    ]