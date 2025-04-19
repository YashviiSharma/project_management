# Copyright (c) 2025, Aman and Yashvi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import now, get_datetime, time_diff_in_seconds, flt
from frappe.model.document import Document

class Task(Document):
    def validate(self):
        self.update_status()
        self.calculate_totals()
        
    def after_insert(self):
        self.update_project()

    def on_update(self):
        self.update_project()
        self.update_deliverable_task()        

    def on_trash(self):
        self.update_project()
        
    def update_status(self):
        if self.progress_ >= 100:
            self.status = "Completed"
        elif self.has_valid_operation():
            self.status = "In Progress"
        elif self.actual_start_date:
            self.status = "Paused"
        else:
            self.status = "Planned"

    def has_valid_operation(self):
        return any(log for log in (self.time_logs or []) if not log.to_time)

    def calculate_totals(self):
        total_mins = 0
        total_completion = 0
        
        for log in (self.time_logs or []):
            if log.from_time and log.to_time:
                duration = time_diff_in_seconds(log.to_time, log.from_time)
                log.time_in_mins = flt(duration / 60, 2)
                total_mins += log.time_in_mins
                
            if hasattr(log, 'completed__of_task') and log.completed__of_task:
                total_completion += log.completed__of_task
                
        self.time_in_minutes = total_mins
        self.progress_ = min(total_completion, 100)

    @frappe.whitelist()
    def start_timer(self):
        if not self.assigned_to:
            frappe.throw("This task is not assigned to any member. Please assign a member first")
            
        if not self.actual_start_date:
            self.actual_start_date = now()

        self.append("time_logs", {
            "member": self.assigned_to,
            "from_time": now(),
            "completed__of_task": 0
        })
        self.status = "In Progress"
        self.save()
        return self

    @frappe.whitelist()
    def pause_timer(self, completed_percent):
        completed_percent = flt(completed_percent)
        
        if not self.time_logs:
            frappe.throw("No time logs found to pause")
        
        previous_completion = sum(
            log.completed__of_task for log in self.time_logs[:-1] 
            if hasattr(log, 'completed__of_task') and log.completed__of_task
        )
        
        # Validate that new completion won't exceed 100%
        if previous_completion + completed_percent > 100:
            frappe.throw(
                f"Total completion will exceed 100%. Current completion: {previous_completion}%, " +
                f"you can add maximum {100 - previous_completion}%"
            )
        
        last_log = self.time_logs[-1]
        last_log.to_time = now()
        last_log.completed__of_task = completed_percent
        
        if last_log.from_time:
            duration = time_diff_in_seconds(last_log.to_time, last_log.from_time)
            last_log.time_in_mins = flt(duration / 60, 2)
        
        self.status = "Paused"
        self.calculate_totals()
        self.save()
        return self

    @frappe.whitelist()
    def resume_timer(self):
        self.append("time_logs", {
            "member": self.assigned_to,
            "from_time": now(),
        })
        self.status = "In Progress"
        self.save()
        return self

    @frappe.whitelist()
    def complete_task(self):
        if not self.time_logs:
            frappe.throw("No time logs found to complete")
        
        # Calculate remaining percentage to reach 100%
        previous_completion = sum(
            log.completed__of_task for log in self.time_logs[:-1] 
            if hasattr(log, 'completed__of_task') and log.completed__of_task
        )
        remaining_percentage = 100 - previous_completion
        
        last_log = self.time_logs[-1]
        last_log.to_time = now()
        last_log.completed__of_task = remaining_percentage
        
        if last_log.from_time:
            duration = time_diff_in_seconds(last_log.to_time, last_log.from_time)
            last_log.time_in_mins = flt(duration / 60, 2)
        
        self.actual_end_date = now()
        self.status = "Completed"
        self.progress_ = 100
        self.calculate_totals()
        self.save()
        return self
    
    def update_project(self):      
        if self.project:
            project = frappe.get_doc("Project", self.project)
            project.update_project_totals()
            project.save()

    def update_deliverable_task(self):
        deliverable_tasks = frappe.get_all("Deliverable Task", filters={"task": self.name})
        for dt in deliverable_tasks:
            frappe.db.set_value("Deliverable Task", dt.name, {
                "status": self.status,
                "progress_": self.progress_
            })