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
            "project_url": f"{get_url()}/app/project/{doc.name}"
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

def send_deliverable_review_notification(doc, method=None):
    """Send notification to client when deliverable status changes to 'Awaiting Client Review'"""
    if doc.status == "Awaiting Client Review":
        project = frappe.get_doc("Project", doc.project)
        
        if not project.client:
            frappe.logger().warning(f"No client associated with project {project.name} for deliverable {doc.name}")
            return
            
        client_name = frappe.db.get_value('User', project.client, 'full_name')
        client_email = frappe.db.get_value('User', project.client, 'email')
        
        if not client_email:
            frappe.logger().warning(f"No email found for client {project.client} for deliverable {doc.name}")
            return
            
        context = {
            "doc": doc.as_dict(),
            "project": project.as_dict(),
            "client_name": client_name,
            "project_name": project.project_name,
            "deliverable_url": f"{get_url()}/frontend/client/deliverables"
        }
        
        subject = f"Deliverable Ready for Review: {doc.deliverable_name}"
        template = frappe.render_template(
            "templates/includes/deliverable_review_notification.html", 
            context
        )
        
        # Send email to client
        try:
            frappe.sendmail(
                recipients=[client_email],
                subject=subject,
                message=template,
            )
            frappe.logger().info(f"Deliverable review notification sent to {client_email} for deliverable {doc.name}")
        except Exception as e:
            frappe.log_error(
                f"Failed to send deliverable review notification email: {str(e)}", 
                "Deliverable Notification"
            )

def send_deliverable_status_change_notification(doc, method=None):
    """
    Send notifications to all assigned users when deliverable status changes 
    from 'Awaiting Client Review' to 'Rejected', 'Approved', or 'Required Changes'
    """
    if not doc.get_doc_before_save():
        return
        
    old_status = doc.get_doc_before_save().status
    new_status = doc.status
    
    if old_status != "Awaiting Client Review" or new_status not in ["Approved", "Rejected", "Required Changes"]:
        return
    
    assigned_users = []
    for task_row in doc.tasks:
        if task_row.assigned_to and task_row.assigned_to not in assigned_users:
            assigned_users.append(task_row.assigned_to)
    
    if not assigned_users:
        frappe.logger().warning(f"No assigned users found for deliverable {doc.name}")
        return
    
    project_name = frappe.db.get_value('Project', doc.project, 'project_name') or doc.project
        
    context = {
        "doc": doc.as_dict(),
        "project_name": project_name,
        "deliverable_name": doc.deliverable_name,
        "status": new_status,
        "deliverable_url": f"{get_url()}/app/deliverable/{doc.name}",
        "submission_date": doc.submission_date,
        "due_date": doc.due_date,
        "reviewed_by": doc.reviewed_by,
        "approved_by": doc.approved_by,
        "changes_made": doc.changes_made or "",
        "timestamp": now()
    }
    
    if new_status == "Approved":
        subject = f"Deliverable Approved: {doc.deliverable_name}"
        template_name = "templates/includes/deliverable_approved_notification.html"
    elif new_status == "Rejected":
        subject = f"Deliverable Rejected: {doc.deliverable_name}"
        template_name = "templates/includes/deliverable_rejected_notification.html" 
    else:  # Required Changes
        subject = f"Deliverable Requires Changes: {doc.deliverable_name}"
        template_name = "templates/includes/deliverable_changes_notification.html"
    
    try:
        template = frappe.render_template(template_name, context)
    except Exception as e:
        frappe.log_error(
            f"Failed to render deliverable status notification template: {str(e)}",
            "Deliverable Notification"
        )
        template = f"""
        <p>Dear User,</p>
        <p>The status of deliverable "{doc.deliverable_name}" has been changed to "{new_status}".</p>
        <p>Please check the deliverable for more details.</p>
        <p>Thank you,<br>System</p>
        """
    
    for user_email in assigned_users:
        try:
            frappe.sendmail(
                recipients=[user_email],
                subject=subject,
                message=template,
            )
            frappe.logger().info(f"Deliverable status notification sent to {user_email} for deliverable {doc.name}")
        except Exception as e:
            frappe.log_error(
                f"Failed to send deliverable status notification email to {user_email}: {str(e)}", 
                "Deliverable Notification"
            )