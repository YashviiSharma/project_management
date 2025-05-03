frappe.query_reports["Member Workload"] = {
    "filters": [
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project"
        },
        {
            "fieldname": "status",
            "label": __("Task Status"),
            "fieldtype": "Select",
            "options": "\nPlanned\nIn Progress\nOn Hold\nPaused\nCompleted\nCancelled"
        },
        {
            "fieldname": "priority",
            "label": __("Priority"),
            "fieldtype": "Select",
            "options": "\nLow\nMedium\nHigh\nCritical"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1)
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today()
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname == "completion_percentage") {
            const percentage = parseFloat(data.completion_percentage || 0);
            let color = "danger";
            
            if (percentage >= 80) color = "success";
            else if (percentage >= 50) color = "info";
            else if (percentage >= 20) color = "warning";
            
            value = `<div class="progress" style="height: 20px; min-width: 100px">
                <div class="progress-bar bg-${color}" role="progressbar" 
                    style="width: ${percentage}%" aria-valuenow="${percentage}" 
                    aria-valuemin="0" aria-valuemax="100">${percentage.toFixed(1)}%</div>
            </div>`;
        }
        
        if (column.fieldname == "high_priority_tasks" && data.high_priority_tasks > 0) {
            const color = data.high_priority_tasks > 3 ? '#d9534f' : '#f0ad4e';
            value = `<span style="color: ${color}; font-weight: bold;">${value}</span>`;
        }
        
        if (column.fieldname == "completed_tasks" && data.completed_tasks > 0) {
            value = `<span style="color: #5cb85c;">${value}</span>`;
        }
        
        if (column.fieldname == "in_progress_tasks" && data.in_progress_tasks > 0) {
            value = `<span style="color: #337ab7;">${value}</span>`;
        }
        
        if (column.fieldname == "on_hold_tasks" && data.on_hold_tasks > 0) {
            value = `<span style="color: #f0ad4e;">${value}</span>`;
        }
        
        if (column.fieldname == "planned_tasks" && data.planned_tasks > 0) {
            value = `<span style="color: #777777;">${value}</span>`;
        }
        
        if (column.fieldname == "full_name") {
            value = `<span style="font-weight: bold;">${value}</span>`;
        }
        
        return value;
    },
    
    onload: function(report) {
        report.page.wrapper.on('click', '.btn-rebuild', function() {
            if (report.chart && report.chart.chart) {
                try {
                    report.chart.chart.destroy();
                } catch (e) {
                    console.log("Chart destruction error handled:", e);
                }
            }
        });
        
        const originalUpdateChart = frappe.views.ReportView.prototype.render_chart;
        frappe.views.ReportView.prototype.render_chart = function() {
            if (this.$chart && this.$chart.find('.chart-container').length) {
                this.$chart.find('.chart-container').empty();
            }
            return originalUpdateChart.apply(this, arguments);
        };
    }
}