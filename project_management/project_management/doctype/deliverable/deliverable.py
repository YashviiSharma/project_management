# Copyright (c) 2025, Aman and Yashvi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate, today, add_days

class Deliverable(Document):
    def validate(self):
        self.validate_due_date()
        
        if self.has_value_changed("status") and self.status == "Awaiting Client Review":
            self.validate_tasks_completion()

    def on_update(self):
        self.update_linked_tasks_end_date()

    def validate_due_date(self):
        if not self.due_date:
            return
            
        due_date = getdate(self.due_date)
        today_date = getdate(today())
        
        project = frappe.get_doc("Project", self.project) if self.project else None
        if not project:
            return
            
        project_start = getdate(project.start_date) if project.start_date else None
        project_end = getdate(project.end_date) if project.end_date else None
        
        earliest_allowed_date = today_date
        if project_start and project_start > today_date:
            earliest_allowed_date = project_start
            
        if due_date < earliest_allowed_date:
            frappe.throw(f"Due date cannot be before {earliest_allowed_date.strftime('%Y-%m-%d')}")
            
        if project_end and due_date >= project_end:
            frappe.throw(f"Due date must be before the project end date ({project_end.strftime('%Y-%m-%d')})")

    def validate_tasks_completion(self):
        if not self.tasks:
            frappe.throw("Cannot send for approval without any tasks")
            
        incomplete_tasks = []
        for task in self.tasks:
            if task.get("progress_", 0) < 100:
                task_name = task.get("task") or task.get("name") or "Unnamed Task"
                progress = task.get("progress_", 0)
                incomplete_tasks.append(f"{task_name} ({progress}%)")
        
        if incomplete_tasks:
            frappe.throw(
                "Cannot send for approval. The following tasks are not 100% complete: " + ", ".join(incomplete_tasks)
            )    

    def update_linked_tasks_end_date(self):
        if not self.due_date or not self.tasks:
            return
            
        task_end_date = add_days(self.due_date, -1)
        updated_tasks = []
        failed_tasks = []
        
        for task_row in self.tasks:
            if not task_row.task:
                continue
                
            try:
                task = frappe.get_doc("Task", task_row.task)
                if getdate(task.end_date) != getdate(task_end_date):
                    task.end_date = task_end_date
                    task.save()
                    updated_tasks.append(task.name)
            except Exception as e:
                error_msg = f"Failed to update task {task_row.task}: {str(e)}"
                failed_tasks.append(error_msg)
                frappe.log_error(error_msg, "Deliverable Task Update Error")
        
        messages = []
        if updated_tasks:
            if len(updated_tasks) == 1:
                messages.append(f"Task `{updated_tasks[0]}` end date updated to {task_end_date}")
            else:
                messages.append(f"{len(updated_tasks)} tasks updated to end on {task_end_date}")
        
        if failed_tasks:
            if len(failed_tasks) == 1:
                messages.append(f"1 task update failed")
            else:
                messages.append(f"{len(failed_tasks)} task updates failed")
        
        if messages:
            indicator = "red" if failed_tasks else "green"
            frappe.msgprint(
                msg="<br>".join(messages),
                title="Task Updates Summary",
                indicator=indicator,
                alert=True
            )
            
            if failed_tasks:
                frappe.log_error("\n".join(failed_tasks), "Deliverable Task Update Errors")