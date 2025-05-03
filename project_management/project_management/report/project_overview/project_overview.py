import frappe
from frappe.query_builder import DocType
from frappe.query_builder.functions import Count, Sum
from pypika import Case

def execute(filters=None):
    # Fetch project data using query builder
    project = DocType("Project")
    team_member = DocType("Team Member")
    task = DocType("Task")
    
    # Main query to get project information
    query = (
        frappe.qb.from_(project)
        .select(
            project.name.as_("project_id"),
            project.project_name.as_("project_name"),
            project.status.as_("status"),
            project.priority.as_("priority"),
            project.start_date.as_("start_date"),
            project.end_date.as_("end_date"),
            project.progress.as_("completion_percentage")
        )
    )
    
    # Apply filter conditions
    if filters:
        if filters.get('from_date') and filters.get('to_date'):
            query = query.where(
                (project.start_date >= filters.get('from_date')) & 
                (project.start_date <= filters.get('to_date'))
            )
        
        if filters.get('status'):
            query = query.where(project.status == filters.get('status'))
        
        if filters.get('priority'):
            query = query.where(project.priority == filters.get('priority'))
        
        if filters.get('user'):
            team_subq = (
                frappe.qb.from_(team_member)
                .select(team_member.parent)
                .where(team_member.user == filters.get('user'))
            )
            query = query.where(project.name.isin(team_subq))
    
    data = query.orderby(project.start_date, order=frappe.qb.desc).run(as_dict=True)
    
    # Get team members for each project
    for row in data:
        # Get assigned team members
        team_members = frappe.get_all(
            "Team Member", 
            filters={"parent": row["project_id"]}, 
            fields=["user"]
        )
        row["assigned_team"] = ", ".join([tm.user for tm in team_members])
        
        # Get task counts
        task_counts = frappe.get_all(
            "Task",
            filters={"project": row["project_id"]},
            fields=[
                "COUNT(name) as total",
                "SUM(IF(status='Completed', 1, 0)) as completed",
                "SUM(IF(status!='Completed', 1, 0)) as pending"
            ]
        )[0]
        
        row["completed_tasks"] = task_counts.completed or 0
        row["pending_tasks"] = task_counts.pending or 0
        row["total_tasks"] = task_counts.total or 0
    
    # Define columns for the report
    columns = [
        {"fieldname": "project_id", "label": "Project ID", "fieldtype": "Link", "options": "Project", "width": 120},
        {"fieldname": "project_name", "label": "Project Name", "fieldtype": "Data", "width": 180},
        {"fieldname": "status", "label": "Status", "fieldtype": "Data", "width": 100},
        {"fieldname": "priority", "label": "Priority", "fieldtype": "Data", "width": 80},
        {"fieldname": "start_date", "label": "Start Date", "fieldtype": "Date", "width": 100},
        {"fieldname": "end_date", "label": "End Date", "fieldtype": "Date", "width": 100},
        {"fieldname": "completion_percentage", "label": "Completion %", "fieldtype": "Percent", "width": 110},
        {"fieldname": "assigned_team", "label": "Assigned Team", "fieldtype": "Data", "width": 200},
        {"fieldname": "pending_tasks", "label": "Pending Tasks", "fieldtype": "Int", "width": 110},
        {"fieldname": "completed_tasks", "label": "Completed Tasks", "fieldtype": "Int", "width": 120}
    ]
    
    # Prepare chart data
    project_names = []
    completed_values = []
    pending_values = []
    
    for i, row in enumerate(data):
        # Task completion data (limit to top 8 projects with tasks)
        if row["total_tasks"] > 0 and len(project_names) < 8:
            project_names.append(row["project_name"])
            completed_values.append(row["completed_tasks"])
            pending_values.append(row["pending_tasks"])
    
    # Chart: Tasks by Project
    chart = {
        "data": {
            "labels": project_names,
            "datasets": [
                {"name": "Completed Tasks", "values": completed_values},
                {"name": "Pending Tasks", "values": pending_values}
            ]
        },
        "type": "bar",
        "height": 300,
        "colors": ["#4caf50", "#ff5252"],
        "title": "Tasks by Project"
    }
    
    # Generate report summary
    total_projects = len(data)
    active_projects = sum(1 for row in data if row["status"] == "In Progress")
    
    total_tasks = sum(row["total_tasks"] for row in data)
    completed_tasks = sum(row["completed_tasks"] for row in data)
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    avg_completion = sum(row["completion_percentage"] or 0 for row in data) / total_projects if total_projects > 0 else 0
    
    report_summary = [
        {"label": "Total Projects", "value": total_projects, "indicator": "blue"},
        {"label": "Active Projects", "value": active_projects, "indicator": "green"},
        {"label": "Total Tasks", "value": total_tasks, "indicator": "blue"},
        {"label": "Tasks Completion Rate", "value": f"{completion_rate:.1f}%", "indicator": "green" if completion_rate > 50 else "orange"},
        {"label": "Avg Project Completion", "value": f"{avg_completion:.1f}%", "indicator": "green" if avg_completion > 50 else "orange"}
    ]
    
    return columns, data, None, chart, report_summary