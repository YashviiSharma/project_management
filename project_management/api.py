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
    task = frappe.get_doc("Task", task_name)
    task.status = status
    task.save()
    frappe.db.commit()
    return "Task Updated"

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
    user_email = frappe.db.get_value("User", frappe.session.user, "email")

    data = frappe.db.sql("""
        SELECT t.task_name, t.progress_
        FROM `tabTask` t
        WHERE t.assigned_to = %s
    """, (user_email,), as_dict=True)

    frappe.logger().info(f"Task Progress Data: {data}")  # Debugging Log

    return {
        "labels": [d["task_name"] for d in data], 
        "datasets": [{"values": [d["progress_"] for d in data]}]
    }