# Copyright (c) 2025, Aman and Yashvi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Deliverable(Document):
    def validate(self):
        if self.has_value_changed("status") and self.status == "Awaiting Client Review":
            self.validate_tasks_completion()

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

