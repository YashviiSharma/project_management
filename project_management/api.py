import frappe


@frappe.whitelist()
def get_assigned_tasks():
    user = frappe.session.user
    user_email = frappe.db.get_value("User", user, "email")

    print(f"\n🔹 Debug: Logged-in User: {user}")
    print(f"🔹 Debug: User Email: {user_email}\n")

    tasks = frappe.get_all(
        "Task", 
        filters={"assigned_to": ["in", [user, user_email]]}, 
        fields=["name", "task_name", "status"]
    )

    print(f"🔹 Debug: Retrieved Tasks: {tasks}\n")

    return tasks

@frappe.whitelist()
def update_task_status(task_name, status):  
    try:
        task = frappe.get_doc("Task", {"task_name": task_name})  
        task.status = status
        
        # Ensure the priority is High if it should be listed in personal tasks
        if status == "In Progress":  
            task.priority = "High"  

        task.save()
        frappe.db.commit()
        return "success"
    except Exception as e:
        frappe.log_error(f"Task Update Error: {str(e)}", "Task Status Update")
        return "error"

@frappe.whitelist()
def get_personal_tasks():
    user = frappe.session.user
    return frappe.get_all("Task", filters={"assigned_to": user, "priority": "High"}, fields=["task_name"])

@frappe.whitelist()
def get_time_tracking():
    user = frappe.session.user
    return frappe.get_all("Task", filters={"assigned_to": user}, fields=["task_name", "time_in_hours"])

@frappe.whitelist()
def get_task_status_chart():
    user = frappe.session.user
    data = frappe.db.sql("""
        SELECT status, COUNT(*) as count
        FROM `tabTask`
        WHERE assigned_to = %s
        GROUP BY status
    """, (user,), as_dict=True)
    
    return {"labels": [d["status"] for d in data], "datasets": [{"values": [d["count"] for d in data]}]}

@frappe.whitelist()
def get_task_progress_chart():
    user = frappe.session.user
    user_email = frappe.db.get_value("User", user, "email")

    data = frappe.db.sql("""
        SELECT name, task_name, progress_
        FROM `tabTask`
        WHERE assigned_to IN (%s, %s) AND status IN ('In Progress', 'Open')
    """, (user, user_email), as_dict=True)

    frappe.logger().info(f"Task Progress Data: {data}")

    return {
        "labels": [d["task_name"] for d in data], 
        "datasets": [{"values": [d["progress_"] for d in data]}]
    }

@frappe.whitelist()
def delete_task(task_name):
    try:
        task = frappe.get_doc("Task", {"task_name": task_name})  # Fetch task by name
        task.delete()  # Delete the task
        frappe.db.commit()
        return "success"
    except Exception as e:
        frappe.log_error(f"Task Deletion Error: {str(e)}", "Task Deletion")
        return "error"
    
@frappe.whitelist()
def get_client_projects():
    """
    Get projects associated with the current logged-in client user
    """
    user = frappe.session.user
    
    # Query for projects where the current user is the client
    projects = frappe.get_all(
        "Project",
        filters={"client": user},
        fields=["name", "project_name", "status", "project_type", "progress", 
                "start_date", "end_date", "raven_channel"]
    )
    
    return projects

@frappe.whitelist()
def get_client_deliverables(projects):
    """
    Get pending deliverables for the client's projects
    """
    if not projects:
        return []
    
    # Ensure the user has access to these projects
    user = frappe.session.user
    
    # For security, filter to only include projects where the user is the client
    authorized_projects = frappe.get_all(
        "Project",
        filters={"client": user, "name": ["in", projects]},
        pluck="name"
    )
    
    if not authorized_projects:
        return []
    
    # Get pending deliverables for authorized projects
    deliverables = frappe.get_all(
        "Deliverable",
        filters={
            "project": ["in", authorized_projects],
            "status": ["in", ["Awaiting Client Review"]]
        },
        fields=["name", "deliverable_name", "project", "status", "due_date", "document"]
    )
    
    return deliverables

@frappe.whitelist()
def get_client_dashboard_stats(projects):
    """
    Get dashboard stats for the client
    """
    if not projects:
        return {
            "active_projects": 0,
            "pending_deliverables": 0,
            "completed_projects": 0
        }
    
    # Ensure the user has access to these projects
    user = frappe.session.user
    
    # For security, filter to only include projects where the user is the client
    authorized_projects = frappe.get_all(
        "Project",
        filters={"client": user, "name": ["in", projects]},
        pluck="name"
    )
    
    if not authorized_projects:
        return {
            "active_projects": 0,
            "pending_deliverables": 0,
            "completed_projects": 0
        }
    
    # Count active projects
    active_projects = frappe.get_all(
        "Project",
        filters={
            "name": ["in", authorized_projects],
            "status": ["in", ["Planned", "In Progress", "On Hold"]]
        },
        as_list=True
    )
    
    # Count pending deliverables
    pending_deliverables = frappe.get_all(
        "Deliverable",
        filters={
            "project": ["in", authorized_projects],
            "status": ["in", ["Awaiting Client Review"]]
        },
        as_list=True
    )
    
    # Count completed projects
    completed_projects = frappe.get_all(
        "Project",
        filters={
            "name": ["in", authorized_projects],
            "status": "Completed"
        },
        as_list=True
    )
    
    return {
        "active_projects": len(active_projects),
        "pending_deliverables": len(pending_deliverables),
        "completed_projects": len(completed_projects)    
    }
