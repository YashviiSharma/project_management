frappe.query_reports["Project Overview"] = {
    "filters": [
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nPlanned\nIn Progress\nOn Hold\nCompleted\nCancelled",
            "default": ""
        },
        {
            "fieldname": "priority",
            "label": __("Priority"),
            "fieldtype": "Select",
            "options": "\nLow\nMedium\nHigh\nCritical",
            "default": ""
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -3)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        },
        {
            "fieldname": "user",
            "label": __("Team Member"),
            "fieldtype": "Link",
            "options": "User"
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname == "priority") {
            if (data.priority == "Critical") {
                value = `<span style="color: red; font-weight: bold;">${value}</span>`;
            } else if (data.priority == "High") {
                value = `<span style="color: orange; font-weight: bold;">${value}</span>`;
            } else if (data.priority == "Medium") {
                value = `<span style="color: #f0ad4e;">${value}</span>`;
            }
        }
        
        if (column.fieldname == "status") {
            if (data.status == "Completed") {
                value = `<span style="color: green; font-weight: bold;">${value}</span>`;
            } else if (data.status == "In Progress") {
                value = `<span style="color: #337ab7; font-weight: bold;">${value}</span>`;
            } else if (data.status == "On Hold") {
                value = `<span style="color: #f0ad4e; font-weight: bold;">${value}</span>`;
            } else if (data.status == "Cancelled") {
                value = `<span style="color: #d9534f; font-weight: bold;">${value}</span>`;
            }
        }
        
        if (column.fieldname == "completion_percentage") {
            const percentage = parseFloat(data.completion_percentage || 0);
            let color = "danger";
            
            if (percentage >= 80) color = "success";
            else if (percentage >= 50) color = "info";
            else if (percentage >= 20) color = "warning";
            
            value = `<div class="progress" style="height: 20px; min-width: 100px">
                <div class="progress-bar bg-${color}" role="progressbar" 
                    style="width: ${percentage}%" aria-valuenow="${percentage}" 
                    aria-valuemin="0" aria-valuemax="100">${percentage}%</div>
            </div>`;
        }
        
        if (column.fieldname == "pending_tasks" && data.pending_tasks > 0) {
            const color = data.pending_tasks > 5 ? '#d9534f' : '#f0ad4e';
            value = `<span style="color: ${color}; font-weight: bold;">${value}</span>`;
        }
        
        if (column.fieldname == "completed_tasks" && data.completed_tasks > 0) {
            value = `<span style="color: #5cb85c;">${value}</span>`;
        }
        
        return value;
    }
}