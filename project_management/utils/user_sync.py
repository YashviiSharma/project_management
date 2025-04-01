import frappe
from frappe import _

def create_raven_user(doc, method):
    if not frappe.db.exists("Raven User", {"user": doc.name}):
        # Enqueue the creation task to be processed in the background
        frappe.enqueue(
            _create_raven_user_in_background,
            user_doc=doc,
            queue="default",
            timeout=300
        )

def _create_raven_user_in_background(user_doc):
    try:
        raven_user = frappe.new_doc("Raven User")
        raven_user.user = user_doc.name
        raven_user.type = "User"
        raven_user.enabled = 1
        raven_user.availability_status = "Available"
        raven_user.full_name = getattr(user_doc, 'full_name', '')
        raven_user.first_name = getattr(user_doc, 'first_name', '')
            
        raven_user.insert(ignore_permissions=True)
        
        frappe.log_error(f"Raven User created successfully for {user_doc.name}", "Raven User Creation Success")
    except Exception as e:
        frappe.log_error(f"Failed to create Raven User for {user_doc.name}: {str(e)}", "Raven User Creation Error")

def update_raven_user(doc, method):
    if frappe.db.exists("Raven User", {"user": doc.name}):
        # Enqueue the update task
        frappe.enqueue(
            _update_raven_user_in_background,
            user_doc=doc,
            queue="default",
            timeout=300
        )

def _update_raven_user_in_background(user_doc):
    try:
        raven_user = frappe.get_doc("Raven User", {"user": user_doc.name})
        original_raven_user = frappe.get_doc("Raven User", {"user": user_doc.name}).as_dict()
        
        raven_user.type = "User"
        raven_user.enabled = 1
        update_raven_fields_from_frappe_user(raven_user, user_doc)
        
        if raven_user.as_dict() != original_raven_user:
            raven_user.save(ignore_permissions=True)
            frappe.log_error(f"Raven User updated successfully for {user_doc.name}", "Raven User Update Success")
    except Exception as e:
        frappe.log_error(f"Failed to update Raven User for {user_doc.name}: {str(e)}", "Raven User Update Error")

def delete_raven_user(doc, method):
    if frappe.db.exists("Raven User", {"user": doc.name}):
        # Enqueue the deletion task
        frappe.enqueue(
            _delete_raven_user_in_background,
            user_name=doc.name,
            queue="default",
            timeout=300
        )

def _delete_raven_user_in_background(user_name):
    try:
        frappe.delete_doc("Raven User", {"user": user_name}, ignore_permissions=True)
        frappe.log_error(f"Raven User deleted successfully for {user_name}", "Raven User Deletion Success")
    except Exception as e:
        frappe.log_error(f"Failed to delete Raven User for {user_name}: {str(e)}", "Raven User Deletion Error")

def update_raven_fields_from_frappe_user(raven_user, frappe_user):
    raven_user.full_name = getattr(frappe_user, 'full_name', '')
    raven_user.first_name = getattr(frappe_user, 'first_name', '')
    
    email = getattr(frappe_user, 'email', None) or getattr(frappe_user, 'username', None)
    if email and hasattr(raven_user, 'email'):
        raven_user.email = email
    
    if hasattr(frappe_user, 'user_image') and frappe_user.user_image:
        raven_user.user_image = frappe_user.user_image
    
    if hasattr(frappe_user, 'user_type'):
        raven_user.type = frappe_user.user_type if frappe_user.user_type else "User"