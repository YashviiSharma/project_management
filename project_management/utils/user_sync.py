import frappe
from frappe import _

def create_raven_user(doc, method):
    if not frappe.db.exists("Raven User", {"user": doc.name}):
        try:
            raven_user = frappe.new_doc("Raven User")
            raven_user.user = doc.name
            
            raven_user.type = "User"
            raven_user.enabled = 1
            
            raven_user.status = "Active"
            raven_user.availability_status = "Available"
            
            # Set any other required fields
            if hasattr(doc, 'full_name'):
                raven_user.full_name = doc.full_name
            if hasattr(doc, 'first_name'):
                raven_user.first_name = doc.first_name
            
            raven_user.insert(ignore_permissions=True)
            
            frappe.msgprint(
                _("Raven User created successfully"),
                title=_("Success"),
                indicator="green"
            )
        except Exception as e:
            frappe.log_error(f"Failed to create Raven User for {doc.name}: {str(e)}")
            frappe.msgprint(
                _("Failed to create Raven User: {0}").format(str(e)),
                title=_("Error"),
                indicator="red"
            )

def update_raven_user(doc, method):
    if frappe.db.exists("Raven User", {"user": doc.name}):
        try:
            raven_user = frappe.get_doc("Raven User", {"user": doc.name})
            original_raven_user = frappe.get_doc("Raven User", {"user": doc.name}).as_dict()
            
            raven_user.type = "User"
            raven_user.enabled = 1
            
            update_raven_fields_from_frappe_user(raven_user, doc)
            
            if raven_user.as_dict() != original_raven_user:
                raven_user.save(ignore_permissions=True)
                frappe.msgprint(
                    _("Raven User updated successfully"),
                    title=_("Success"),
                    indicator="green"
                )
        except Exception as e:
            frappe.log_error(f"Failed to update Raven User for {doc.name}: {str(e)}")
            frappe.msgprint(
                _("Failed to update Raven User: {0}").format(str(e)),
                title=_("Error"),
                indicator="red"
            )

def delete_raven_user(doc, method):
    if frappe.db.exists("Raven User", {"user": doc.name}):
        try:
            frappe.delete_doc("Raven User", {"user": doc.name}, ignore_permissions=True)
            frappe.msgprint(
                _("Raven User deleted successfully"),
                title=_("Success"),
                indicator="green"
            )
        except Exception as e:
            frappe.log_error(f"Failed to delete Raven User for {doc.name}: {str(e)}")
            frappe.msgprint(
                _("Failed to delete Raven User: {0}").format(str(e)),
                title=_("Error"),
                indicator="red"
            )

def update_raven_fields_from_frappe_user(raven_user, frappe_user):
    raven_user.full_name = getattr(frappe_user, 'full_name', '')
    raven_user.first_name = getattr(frappe_user, 'first_name', '')
    
    email = getattr(frappe_user, 'email', None) or getattr(frappe_user, 'username', None)
    if email and hasattr(raven_user, 'email'):
        raven_user.email = email
        
    raven_user.status = "Active"
    
    if hasattr(frappe_user, 'user_image') and frappe_user.user_image:
        raven_user.user_image = frappe_user.user_image
    
    if hasattr(frappe_user, 'user_type'):
        raven_user.type = frappe_user.user_type if frappe_user.user_type else "User"


