# Copyright (c) 2025, Aman and Yashvi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _

class Project(Document):
    def before_save(self):
        if not self.start_date:
            self.start_date = frappe.utils.today()
        
        if not self.end_date and self.start_date:
            start_date = frappe.utils.getdate(self.start_date)
            self.end_date = frappe.utils.add_days(start_date, 180)
    
    def validate(self):
        if not self.is_new() and not self.raven_channel:
            self.create_raven_channel()
        self.update_project_totals()
        self.update_project_status()

    def after_insert(self):
        self.create_raven_channel()

    def on_update(self):
        self.sync_channel_members()

    def get_default_raven_workspace(self):
        project_workspace = frappe.db.get_value("Raven Workspace", {"workspace_name": "Project"})
        
        if project_workspace:
            return project_workspace
            
        if frappe.db.exists("DocType", "Raven Workspace"):
            try:
                workspace = frappe.new_doc("Raven Workspace")
                workspace.workspace_name = "Project"
                workspace.type = "Private"
                workspace.insert(ignore_permissions=True)
                frappe.msgprint(_("Created default 'Project' workspace for Raven channels"), alert=True)
                return workspace.name
            except Exception as e:
                frappe.log_error(f"Failed to create Raven workspace: {str(e)}")
                return None
        
        return None

    def create_raven_channel(self):
        if self.raven_channel and frappe.db.exists("Raven Channel", self.raven_channel):
            return self.raven_channel

        if not frappe.db.exists("DocType", "Raven Channel"):
            frappe.msgprint(_("Raven messaging app is not installed. Channel creation skipped."), alert=True)
            return None

        try:
            workspace = self.get_default_raven_workspace()
            if not workspace:
                frappe.msgprint(_("Could not setup messaging workspace for this project"), alert=True)
                return None

            channel_name = self.project_name
            channel_id = f"{workspace}-{frappe.scrub(self.project_name)}"

            channel = frappe.new_doc("Raven Channel")
            channel.update({
                "channel_name": channel_name,
                "type": "Private",
                "channel_admin": frappe.session.user,
                "linked_doctype": "Project",
                "linked_document": self.name,
                "workspace": workspace
            })
            
            channel.insert(ignore_permissions=True)
            frappe.db.set_value("Raven Channel", channel.name, "name", channel_id)
            channel = frappe.get_doc("Raven Channel", channel_id)
            
            self._add_channel_members(channel_id)
            
            self.db_set("raven_channel", channel_id, update_modified=False)
            self.reload()
            
            frappe.db.commit()
            
            frappe.msgprint(
                _("Channel created successfully for the project '{0}'").format(self.project_name),
                alert=True,
                indicator="green"
            )
            
            return channel_id

        except Exception as e:
            error_message = f"Channel creation failed for project {self.name}: {str(e)}"
            frappe.log_error(title="Channel Creation Failed", message=error_message)
            
            frappe.msgprint(
                _("Failed to create project channel. System error: {0}").format(str(e)),
                alert=True,
                indicator="red"
            )
            return None
            
    def _add_channel_members(self, channel_id):
        if not channel_id or not frappe.db.exists("Raven Channel", channel_id):
            return
            
        members = set()
        
        if self.client and frappe.db.exists("User", self.client):
            members.add(self.client)
        
        if self.team_member:
            for member in self.team_member:
                if member.user and frappe.db.exists("User", member.user):
                    members.add(member.user)
        
        members.add(frappe.session.user)

        for user in members:
            try:
                if not frappe.db.exists("Raven Channel Member", {"channel_id": channel_id, "user_id": user}):
                    member_doc = frappe.new_doc("Raven Channel Member")
                    member_doc.update({
                        "channel_id": channel_id,
                        "user_id": user,
                        "is_admin": 1 if user == frappe.session.user else 0,
                        "allow_notifications": 1
                    })
                    member_doc.insert(ignore_permissions=True)
                    frappe.msgprint(_("Added {0} to project channel").format(user), alert=True)
            except Exception as e:
                frappe.log_error(f"Failed to add member {user} to channel", "Channel Member Error")

    def sync_channel_members(self):
        if not self.raven_channel:
            return
            
        try:
            self._add_channel_members(self.raven_channel)
            
            current_members = frappe.get_all(
                "Raven Channel Member", 
                filters={"channel_id": self.raven_channel},
                fields=["user_id", "is_admin"]
            )
            current_member_ids = {m.user_id: m.is_admin for m in current_members}
            
            expected_members = set()
            if self.client:
                expected_members.add(self.client)
                
            if self.team_member:
                for member in self.team_member:
                    if member.user:
                        expected_members.add(member.user)
            
            expected_members.add(frappe.session.user)
            
            for user_id in current_member_ids:
                if user_id not in expected_members and not current_member_ids[user_id]:
                    frappe.db.delete(
                        "Raven Channel Member", 
                        {"channel_id": self.raven_channel, "user_id": user_id}
                    )
                    frappe.msgprint(_("Removed {0} from project channel").format(user_id), alert=True)
        
        except Exception as e:
            frappe.log_error(
                message=f"Channel member sync failed: {str(e)}",
                title="Member Sync Error"
            )

    # Update project time and progress_ based on linked tasks
    def update_project_totals(self):
        
        tasks = frappe.get_all("Task",
            filters={"project": self.name},
            fields=["time_in_minutes", "progress_"]
        )
        
        if tasks:
            total_minutes = sum(task.time_in_minutes or 0 for task in tasks)
            self.time_in_hours = total_minutes / 60
            
            total_progress = sum(task.progress_ or 0 for task in tasks)
            self.progress_ = total_progress / len(tasks)
        
    def update_project_status(self):
        if not hasattr(self, 'progress_') or self.progress_ is None:
            self.progress_ = 0
            
        if self.progress_ == 0:
            self.status = "Planned"
        elif 0 < self.progress_ < 100:
            self.status = "In Progress"
        elif self.progress_ == 100:
            self.status = "Completed"