import frappe
from frappe import _
from frappe.utils import get_url, now

def send_project_approval_email(doc, method=None):
    send_vendor_notifications(doc)
    send_team_member_notifications(doc)

def send_vendor_notifications(doc):
    """Send notifications to all vendors associated with the project"""
    # Filter out vendors from team members
    vendors = [member for member in doc.team_member if member.is_vendor]
    
    if not vendors:
        return
    
    for vendor in vendors:
        context = {
            "doc": doc.as_dict(),
            "vendor_name": vendor.full_name,
            "vendor_email": vendor.email,
            "client_name": frappe.db.get_value('User', doc.client, 'full_name'),
            "client_email": frappe.db.get_value('User', doc.client, 'email'),
            "project_url": f"{get_url()}/frontend/vendor/projects/{doc.name}"
        }
        
        # Render vendor notification template
        subject = f"Vendor Assignment: {doc.project_name}"
        template = frappe.render_template(
            "templates/includes/vendor_project_notification.html", 
            context
        )
        
        # Send email to vendor
        try:
            frappe.sendmail(
                recipients=[vendor.email],
                subject=subject,
                message=template,
            )
            frappe.logger().info(f"Project vendor notification sent to {vendor.email} for project {doc.name}")
        except Exception as e:
            frappe.log_error(
                f"Failed to send vendor notification email: {str(e)}", 
                "Project Notification"
            )

def send_team_member_notifications(doc):
    """Send notifications to all internal team members associated with the project"""
    # Filter out internal team members
    team_members = [member for member in doc.team_member if not member.is_vendor]
    
    if not team_members:
        return
    
    for member in team_members:
        context = {
            "doc": doc.as_dict(),
            "member_name": member.full_name,
            "member_email": member.email,
            "client_name": frappe.db.get_value('User', doc.client, 'full_name'),
            "client_email": frappe.db.get_value('User', doc.client, 'email'),
            "project_url": f"{get_url()}/frontend/client/projects/{doc.name}"
        }
        
        # Render team member notification template
        subject = f"Team Assignment: {doc.project_name}"
        template = frappe.render_template(
            "templates/includes/member_project_notification.html", 
            context
        )
        
        # Send email to team member
        try:
            frappe.sendmail(
                recipients=[member.email],
                subject=subject,
                message=template,
            )
            frappe.logger().info(f"Project team member notification sent to {member.email} for project {doc.name}")
        except Exception as e:
            frappe.log_error(
                f"Failed to send team member notification email: {str(e)}", 
                "Project Notification"
            )
