import frappe

def login_redirection():
    user = frappe.session.user
    
    if user == "Administrator":
        frappe.local.response['home_page'] = "/app"
        return
    
    user_roles = frappe.get_roles(user)
    
    if "Project Manager" in user_roles:
        frappe.local.response['home_page'] = "app/project"
    elif "Team Member" in user_roles:
        user_email = frappe.db.get_value("User", user, "email")
        frappe.local.response['home_page'] = f"app/task?assigned_to={user_email}"
    elif "Client" in user_roles:
        frappe.local.response['home_page'] = "frontend/client/dashboard"
    elif "Vendor" in user_roles:
        frappe.local.response['home_page'] = "frontend/vendor/dashboard"
    else:
        # Default redirect if none of the specified roles
        frappe.local.response['home_page'] = "/frontend"