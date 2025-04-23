import frappe
from frappe import _
from frappe.utils.file_manager import save_file
from frappe.model.workflow import apply_workflow

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
		task = frappe.get_doc("Task", {"task_name": task_name}) 
		task.delete()  
		frappe.db.commit()
		return "success"
	except Exception as e:
		frappe.log_error(f"Task Deletion Error: {str(e)}", "Task Deletion")
		return "error"
	
@frappe.whitelist()
def get_client_projects():
    """
    Get projects associated with the current logged-in client user
    and also projects of users who invited the current user
    """
    user = frappe.session.user
    
    # Get user's own projects
    projects = frappe.get_all(
        "Project",
        filters={"client": user},
        fields=["name", "project_name", "status", "project_type", "progress", 
                "start_date", "end_date", "raven_channel"]
    )
    
    # Get projects from inviters where the current user has accepted invitations
    invitations = frappe.get_all(
        "PM Client Invitation",
        filters={
            "email": user,
            "status": "Accepted"
        },
        fields=["invited_by", "projects"]
    )
    
    # Add projects from inviters
    for invitation in invitations:
        if invitation.projects:
            invited_projects = frappe.parse_json(invitation.projects)
            invited_project_details = frappe.get_all(
                "Project",
                filters={"name": ["in", invited_projects]},
                fields=["name", "project_name", "status", "project_type", "progress", 
                        "start_date", "end_date", "raven_channel"]
            )
            projects.extend(invited_project_details)
    
    return projects

@frappe.whitelist()
def get_client_deliverables(projects):
    """
    Get pending deliverables for the client's projects and invited projects
    """
    if not projects:
        return []
    
    user = frappe.session.user
    
    # Get projects the user directly owns
    own_projects = frappe.get_all(
        "Project",
        filters={"client": user, "name": ["in", projects]},
        pluck="name"
    )
    
    # Get projects the user has been invited to
    invited_projects = []
    invitations = frappe.get_all(
        "PM Client Invitation",
        filters={
            "email": user,
            "status": "Accepted"
        },
        fields=["projects"]
    )
    
    for invitation in invitations:
        if invitation.projects:
            invited_project_list = frappe.parse_json(invitation.projects)
            invited_projects.extend([p for p in invited_project_list if p in projects])
    
    # Combine own and invited projects
    authorized_projects = list(set(own_projects + invited_projects))
    
    if not authorized_projects:
        return []
    
    deliverables = frappe.get_all(
        "Deliverable",
        filters={
            "project": ["in", authorized_projects],
        },
        fields=["name", "deliverable_name", "project", "status", "due_date", "document"]
    )
    
    return deliverables

@frappe.whitelist()
def get_client_dashboard_stats(projects):
    """
    Get dashboard stats for the client including invited projects
    """
    if not projects:
        return {
            "active_projects": 0,
            "pending_deliverables": 0,
            "completed_projects": 0
        }
    
    user = frappe.session.user
    
    # Get projects the user directly owns
    own_projects = frappe.get_all(
        "Project",
        filters={"client": user, "name": ["in", projects]},
        pluck="name"
    )
    
    # Get projects the user has been invited to
    invited_projects = []
    invitations = frappe.get_all(
        "PM Client Invitation",
        filters={
            "email": user,
            "status": "Accepted"
        },
        fields=["projects"]
    )
    
    for invitation in invitations:
        if invitation.projects:
            invited_project_list = frappe.parse_json(invitation.projects)
            invited_projects.extend([p for p in invited_project_list if p in projects])
    
    # Combine own and invited projects
    authorized_projects = list(set(own_projects + invited_projects))
    
    if not authorized_projects:
        return {
            "active_projects": 0,
            "pending_deliverables": 0,
            "completed_projects": 0
        }
    
    active_projects = frappe.get_all(
        "Project",
        filters={
            "name": ["in", authorized_projects],
            "status": ["in", ["Planned", "In Progress", "On Hold"]]
        },
        as_list=True
    )
    
    pending_deliverables = frappe.get_all(
        "Deliverable",
        filters={
            "project": ["in", authorized_projects],
            "status": ["in", ["Awaiting Client Review"]]
        },
        as_list=True
    )
    
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

@frappe.whitelist()
def submit_deliverable_review(deliverable, comment, action):
	try:
		user = frappe.session.user
		deliverable_doc = frappe.get_doc("Deliverable", deliverable)
		project = frappe.get_doc("Project", deliverable_doc.project)
		
		if project.client != user:
			return {"status": "error", "message": "You don't have permission to review this deliverable"}
		
		workflow_action = action  
		
		workflow = frappe.get_doc("Workflow", {"document_type": "Deliverable", "is_active": 1})
		transition = next(
			(t for t in workflow.transitions 
			 if t.state == deliverable_doc.workflow_state and t.action == workflow_action),
			None
		)
		
		if not transition:
			return {
				"status": "error", 
				"message": f"Cannot perform action '{action}' from current state '{deliverable_doc.workflow_state}'"
			}
		
		deliverable_doc.workflow_state = transition.next_state
		
		state_doc = next(
			(s for s in workflow.states 
			 if s.state == transition.next_state),
			None
		)
		
		if state_doc and state_doc.update_field == "status":
			deliverable_doc.status = state_doc.update_value
		
		deliverable_doc.save(ignore_permissions=True)
		
		if comment:
			content = f"Client Review ({action}): {comment}"
		else:
			content = f"Client Review ({action}): <i>{user} updated the status to {action}</i>"

		comment_doc = frappe.get_doc({
			"doctype": "Comment",
			"comment_type": "Comment",
			"reference_doctype": "Deliverable",
			"reference_name": deliverable,
			"content": content,
			"comment_by": user
		})
		comment_doc.insert(ignore_permissions=True)

		frappe.logger().info(f"Client {user} reviewed deliverable {deliverable} as {action}")
		
		return {
			"status": "success", 
			"message": f"Client {user} reviewed deliverable {deliverable} as {action}",
			"deliverable": deliverable_doc.name
		}
		
	except Exception as e:
		frappe.log_error(f"Deliverable Review Error: {str(e)}", "Deliverable Review")
		return {
			"status": "error", 
			"message": f"Error submitting review: {str(e)}"
		}
	
@frappe.whitelist()
def get_project_team_members(projects):
    """
    Get all team members working on the client's projects including invited projects
    """
    if isinstance(projects, str):
        import json
        try:
            parsed_data = json.loads(projects)
            if isinstance(parsed_data, list):
                projects = parsed_data
            elif isinstance(parsed_data, dict) and 'projects' in parsed_data:
                projects = parsed_data['projects']
            else:
                projects = [projects]
        except json.JSONDecodeError:
            projects = [projects]
    elif isinstance(projects, dict) and 'projects' in projects:
        projects = projects['projects']
        
    if not projects:
        return {"members": [], "project_members": {}}
    
    user = frappe.session.user
    
    # Get projects the user directly owns
    own_projects = frappe.get_all(
        "Project",
        filters={"client": user, "name": ["in", projects]},
        pluck="name"
    )
    
    # Get projects the user has been invited to
    invited_projects = []
    invitations = frappe.get_all(
        "PM Client Invitation",
        filters={
            "email": user,
            "status": "Accepted"
        },
        fields=["projects"]
    )
    
    for invitation in invitations:
        if invitation.projects:
            invited_project_list = frappe.parse_json(invitation.projects)
            invited_projects.extend([p for p in invited_project_list if p in projects])
    
    # Combine own and invited projects
    authorized_projects = list(set(own_projects + invited_projects))
    
    if not authorized_projects:
        return {"members": [], "project_members": {}}
    
    project_members = {}
    members = set()
    
    for project in authorized_projects:
        try:
            project_doc = frappe.get_doc("Project", project)
            
            project_team = []
            if hasattr(project_doc, 'team_member') and project_doc.team_member:
                project_team = [d.user for d in project_doc.team_member if d.user]
            elif hasattr(project_doc, 'users') and project_doc.users:
                project_team = [d.user for d in project_doc.users if d.user]
            
            tasks = frappe.get_all("Task", filters={"project": project}, fields=["name", "assigned_to"])
            task_members = [t.assigned_to for t in tasks if t.assigned_to]
            
            all_members = list(set(project_team + task_members))
            
            all_members = [m for m in all_members if m]
            
            project_members[project] = all_members
            members.update(all_members)
        except Exception as e:
            frappe.log_error(f"Error processing project {project}: {str(e)}", 
                           "Team Member Fetch Error")
    
    member_details = []
    for member in members:
        try:
            user_doc = frappe.get_doc("User", member)
            member_details.append({
                "name": member,
                "full_name": user_doc.full_name or user_doc.name,
                "email": user_doc.email,
                "mobile_no": user_doc.mobile_no if hasattr(user_doc, 'mobile_no') else None,
                "designation": user_doc.designation if hasattr(user_doc, 'designation') else None,
                "department": user_doc.department if hasattr(user_doc, 'department') else None
            })
        except Exception as e:
            frappe.log_error(f"Error fetching team member details for {member}: {str(e)}", 
                            "Team Member Fetch Error")
    
    return {
        "members": member_details,
        "project_members": project_members
    }

@frappe.whitelist()
def get_client_project_details(project):
    """
    Get detailed information about a specific project for the client or invited user
    """
    user = frappe.session.user
    
    # Check if the user directly owns the project
    is_owner = frappe.db.exists(
        "Project", 
        {"name": project, "client": user}
    )
    
    # Check if the user has been invited to this project
    is_invited = False
    if not is_owner:
        invitations = frappe.get_all(
            "PM Client Invitation",
            filters={
                "email": user,
                "status": "Accepted"
            },
            fields=["projects"]
        )
        
        for invitation in invitations:
            if invitation.projects:
                invited_projects = frappe.parse_json(invitation.projects)
                if project in invited_projects:
                    is_invited = True
                    break
    
    if not (is_owner or is_invited):
        frappe.logger().info(f"User {user} attempted to access unauthorized project {project}")
        return None
    
    try:
        project_doc = frappe.get_doc("Project", project)
        
        project_data = {
            "name": project_doc.name,
            "project_name": project_doc.project_name,
            "status": project_doc.status,
            "project_type": project_doc.project_type,
            "priority": project_doc.priority,
            "progress": project_doc.progress,
            "start_date": project_doc.start_date,
            "end_date": project_doc.end_date,
            "description": project_doc.description,
            "document": project_doc.document,
            "raven_channel": project_doc.raven_channel,
            "department": project_doc.get("department") if hasattr(project_doc, "department") else None
        }
        
        return project_data
        
    except Exception as e:
        frappe.log_error(f"Error fetching project details for {project}: {str(e)}", 
                        "Project Details Fetch Error")
        return None
 
@frappe.whitelist(allow_guest=False)
def get_assigned_tasks_for_vendor():
	user_email = frappe.session.user

	project_links = frappe.get_all(
		"Team Member",
		filters={"user": user_email},
		fields=["parent"]
	)
	project_ids = [p["parent"] for p in project_links]

	if project_ids:
		tasks = frappe.get_all(
			"Task",
			filters={"project": ["in", project_ids]},
			fields=[
				"name",       
				"task_name",    
				"status",
				"start_date",
				"end_date",
				"project",
				"assigned_to",
				"progress_",
				"priority"
			]
		)
	else:
		tasks = []

	return tasks


@frappe.whitelist()
def get_pending_deliverables_for_vendor():
    user_email = frappe.session.user

    task_deliverables = frappe.get_all(
        "Deliverable Task",
        filters={
            "assigned_to": user_email,
            "progress_": 100
        },
        fields=["parent"],
        distinct=True
    )

    deliverable_names = list(set(d["parent"] for d in task_deliverables))
    if not deliverable_names:
        return []

    deliverables = frappe.get_all(
        "Deliverable",
        filters={
            "name": ["in", deliverable_names],
        },
        fields=[
            "name",
            "deliverable_name",
            "project",
            "status",
            "due_date",
            "priority",
            "submission_date"
        ],
        order_by="due_date asc"
    )

    return deliverables


@frappe.whitelist(allow_guest=False)
def submit_deliverable():
	try:
		deliverable_name = frappe.form_dict.get("deliverable")
		description = frappe.form_dict.get("description")
		file = frappe.request.files.get("file")

		if not deliverable_name:
			frappe.throw(_("Deliverable name is required"))

		doc = frappe.get_doc("Deliverable", deliverable_name)

		if description:
			doc.description = description

		if file:
			saved_file = save_file(
				fname=file.filename,
				content=file.stream.read(),
				dt=doc.doctype,
				dn=doc.name,
				folder=None,
				decode=False,
				is_private=1
			)
			doc.append("attachments", {
				"file": saved_file.file_url
			})
		workflow = frappe.get_doc("Workflow", {"document_type": "Deliverable", "is_active": 1})
		transition = next(
			(t for t in workflow.transitions 
			 if t.state == doc.workflow_state and t.action == "Submit for Approval"),
			None
		)
		if not transition:
			frappe.throw(_("No valid workflow transition found from state '{0}' using action 'Submit for Approval'").format(doc.workflow_state))

		doc.workflow_state = transition.next_state
		doc.flags.ignore_permissions = True
		doc.flags.ignore_validate = True
		doc.flags.ignore_validate_update_after_submit = True
		doc.flags.ignore_workflow_validation = True
		doc.save()
		return {"message": "Deliverable submitted successfully"}

	except frappe.DoesNotExistError:
		frappe.throw(_("The deliverable does not exist"))
	except Exception as e:
		frappe.log_error(frappe.get_traceback(), "Submit Deliverable Error")
		frappe.throw(_("Error: ") + str(e))

@frappe.whitelist(allow_guest=True) 
def get_single_task(task_name):
    task = frappe.get_all('Task', filters={'name': task_name}, fields=[
        'name', 'assigned_to', 'end_date', 'priority', 'status', 'progress_',
        'description'])  
    if task:
        return task[0]  
    else:
        return {"message": "Task not found"} 
	
@frappe.whitelist(allow_guest=True)
def accept_invitation(key: str = None):
    if not key:
        frappe.throw("Invalid or expired key")
    
    result = frappe.db.get_all("PM Client Invitation", filters={"key": key}, pluck="name")
    if not result:
        frappe.throw("Invalid or expired key")
    
    invitation = frappe.get_doc("PM Client Invitation", result[0])
    
    invitation.accept()
    invitation.reload()
    
    user = frappe.get_doc("User", invitation.email)
    needs_password_setup = user and not user.last_password_reset_date
    
    if invitation.status == "Accepted":
        if needs_password_setup:
            url = invitation.get_password_link()
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = f"{url}"
        else:
            frappe.local.login_manager.login_as(invitation.email)
            frappe.local.response["type"] = "redirect"
            frappe.local.response["location"] = "/frontend"


@frappe.whitelist()
def invite_by_email(emails, role):
    if not emails:
        return {"status": "error", "message": "No email provided"}
    
    user = frappe.session.user
    
    user_roles = frappe.get_roles(user)
    if "Client" not in user_roles:
        return {"status": "error", "message": "Only Clients can send invitations"}
    
    client_projects = frappe.get_all(
        "Project", 
        filters={"client": user},
        pluck="name"
    )
    
    if not client_projects:
        return {"status": "error", "message": "You don't have any projects to share"}
    
    # Validate role
    if role not in ["Client", "Guest"]:
        return {"status": "error", "message": "Invalid role selected"}
    
    email_list = frappe.utils.split_emails(emails)
    
    # Check for existing users or pending invitations
    existing_members = frappe.db.get_all("User", filters={"email": ["in", email_list]}, pluck="email")
    existing_invites = frappe.db.get_all(
        "PM Client Invitation",
        filters={
            "email": ["in", email_list],
            "status": "Pending"
        },
        pluck="email"
    )
    
    to_invite = list(set(email_list) - set(existing_invites))
    
    # Collect emails with pending invitations
    pending_invites = list(set(email_list).intersection(set(existing_invites)))
    
    projects_json = frappe.as_json(client_projects, indent=None)
    
    invitations_sent = []
    
    for email in to_invite:
        try:
            invitation = frappe.get_doc(
                doctype="PM Client Invitation", 
                email=email, 
                role=role, 
                projects=projects_json
            )
            invitation.insert(ignore_permissions=True)
            invitations_sent.append(email)
        except Exception as e:
            frappe.log_error(f"Failed to create invitation for {email}: {str(e)}", "Client Invitation")
    
    # Create appropriate message
    message_parts = []
    if invitations_sent:
        message_parts.append(f"Invitations sent to {len(invitations_sent)} email(s)")
    
    if pending_invites:
        message_parts.append(f"{len(pending_invites)} email(s) already have pending invitations")
    
    message = ". ".join(message_parts)
    
    return {
        "status": "success" if invitations_sent else "info", 
        "message": message,
        "invitations_sent": invitations_sent,
        "pending_invites": pending_invites
    }


@frappe.whitelist()
def get_client_invitations():
    """Get all invitations sent by the current client"""
    user = frappe.session.user
    
    invitations = frappe.get_all(
        "PM Client Invitation",
        filters={"invited_by": user},
        fields=["name", "email", "role", "status", "email_sent_at", "accepted_at"],
        order_by="creation desc"
    )
    
    return invitations


# Add this function to check if a user is accessing as a guest of another client
def get_client_for_guest(user=None):
    """
    If the user is a guest, returns the client they have access to
    Otherwise returns None
    """
    if not user:
        user = frappe.session.user
    
    guest_access = frappe.get_all(
        "PM Client Guest Access",
        filters={"user": user},
        fields=["client"],
        limit=1
    )
    
    if guest_access:
        return guest_access[0].client
    
    return None
