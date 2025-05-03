# Copyright (c) 2025, Aman and Yashvi and contributors
# For license information, please see license.txt

import frappe
from frappe.utils import getdate, flt, cint, today, add_days

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    summary = get_report_summary(data)
    
    return columns, data, None, chart, summary

def get_columns():
    return [
        {"fieldname": "deliverable_id", "label": "ID", "fieldtype": "Link", "options": "Deliverable", "width": 90},
        {"fieldname": "deliverable_name", "label": "Deliverable Name", "fieldtype": "Data", "width": 180},
        {"fieldname": "project", "label": "Project", "fieldtype": "Link", "options": "Project", "width": 120},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 130},
        {"fieldname": "priority", "label": "Priority", "fieldtype": "Data", "width": 90},
        {"fieldname": "due_date", "label": "Due Date", "fieldtype": "Date", "width": 100},
        {"fieldname": "days_left", "label": "Days Left", "fieldtype": "Int", "width": 90},
        {"fieldname": "submission_date", "label": "Submission Date", "fieldtype": "Date", "width": 120},
        {"fieldname": "tasks_count", "label": "Tasks", "fieldtype": "Int", "width": 70},
        {"fieldname": "tasks_completed", "label": "Tasks Completed", "fieldtype": "Int", "width": 130},
        {"fieldname": "completion_percent", "label": "Completion %", "fieldtype": "Percent", "width": 110},
        {"fieldname": "reviewed_by", "label": "Reviewed By", "fieldtype": "Data", "width": 120},
        {"fieldname": "approved_by", "label": "Approved By", "fieldtype": "Data", "width": 120}
    ]

def get_data(filters):
    conditions = get_conditions(filters)
    
    deliverables = frappe.get_all(
        "Deliverable",
        filters=conditions,
        fields=[
            "name as deliverable_id", "deliverable_name", "project", 
            "status", "priority", "due_date", "submission_date",
            "reviewed_by", "approved_by"
        ],
        order_by="due_date asc"
    )
    
    data = []
    today_date = getdate(today())
    
    for d in deliverables:
        if d.due_date:
            due_date = getdate(d.due_date)
            d.days_left = (due_date - today_date).days
        else:
            d.days_left = None
            
        tasks = get_deliverable_tasks(d.deliverable_id)
        d.tasks_count = len(tasks)
        d.tasks_completed = sum(1 for task in tasks if task.status == "Completed")
        
        if d.tasks_count:
            d.completion_percent = flt(d.tasks_completed) / flt(d.tasks_count) * 100
        else:
            if d.status == "Approved":
                d.completion_percent = 100
            elif d.status == "Rejected":
                d.completion_percent = 100  
            elif d.status == "Awaiting Client Review":
                d.completion_percent = 90 
            elif d.status == "Required Changes":
                d.completion_percent = 75
            elif d.status == "In Progress":
                d.completion_percent = 50  
            else:
                d.completion_percent = 0
        
        data.append(d)
        
    return data

def get_conditions(filters):
    conditions = {}
    
    if filters:
        if filters.get("project"):
            conditions["project"] = filters.get("project")
            
        if filters.get("status"):
            conditions["status"] = filters.get("status")
            
        if filters.get("priority"):
            conditions["priority"] = filters.get("priority")
            
        if filters.get("from_date") and filters.get("to_date"):
            conditions["due_date"] = ["between", [filters.get("from_date"), filters.get("to_date")]]
        elif filters.get("from_date"):
            conditions["due_date"] = [">=", filters.get("from_date")]
        elif filters.get("to_date"):
            conditions["due_date"] = ["<=", filters.get("to_date")]
        
        if cint(filters.get("overdue")):
            conditions["due_date"] = ["<", today()]
    
    return conditions

def get_deliverable_tasks(deliverable_id):
    return frappe.get_all(
        "Deliverable Task",
        filters={"parent": deliverable_id},
        fields=["task", "status", "progress_"]
    )

def get_chart_data(data):
    if not data:
        return None
        
    status_map = {
        "In Progress": 0,
        "Awaiting Client Review": 0,
        "Required Changes": 0,
        "Approved": 0,
        "Rejected": 0
    }
    
    for d in data:
        if d.status in status_map:
            status_map[d.status] += 1
        else:
            status_map["In Progress"] += 1
    
    chart = {
        "data": {
            "labels": list(status_map.keys()),
            "datasets": [{"name": "Status Count", "values": list(status_map.values())}]
        },
        "type": "pie",
        "height": 280,
        "colors": ["#5e64ff", "#ffa00a", "#ff5858", "#28a745", "#dc3545"]
    }
    
    return chart

def get_report_summary(data):
    if not data:
        return []
        
    total_deliverables = len(data)
    overdue = sum(1 for d in data if d.due_date and getdate(d.due_date) < getdate(today()))
    
    status_counts = {
        "In Progress": sum(1 for d in data if d.status == "In Progress"),
        "Awaiting Client Review": sum(1 for d in data if d.status == "Awaiting Client Review"),
        "Required Changes": sum(1 for d in data if d.status == "Required Changes"),
        "Approved": sum(1 for d in data if d.status == "Approved"),
        "Rejected": sum(1 for d in data if d.status == "Rejected")
    }
    
    total_completion = sum(d.completion_percent for d in data)
    avg_completion = total_completion / total_deliverables if total_deliverables else 0
    
    return [
        {"label": "Total Deliverables", "value": total_deliverables, "indicator": "blue"},
        {"label": "Overdue", "value": overdue, "indicator": "red"},
        {"label": "Approved", "value": status_counts["Approved"], "indicator": "green"},
        {"label": "In Progress", "value": status_counts["In Progress"], "indicator": "orange"},
        {"label": "Avg. Completion", "value": f"{avg_completion:.1f}%", "indicator": "blue"}
    ]