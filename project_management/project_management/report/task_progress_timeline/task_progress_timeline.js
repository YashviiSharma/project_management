// Copyright (c) 2025, Aman and Yashvi and contributors
// For license information, please see license.txt

frappe.query_reports["Task Progress Timeline"] = {
	"filters": [
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "width": "100px"
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nPlanned\nIn Progress\nOn Hold\nPaused\nCompleted\nCancelled",
            "width": "100px"
        },
        {
            "fieldname": "priority",
            "label": __("Priority"),
            "fieldtype": "Select",
            "options": "\nLow\nMedium\nHigh\nCritical",
            "width": "100px"
        },
        {
            "fieldname": "assigned_to",
            "label": __("Assigned To"),
            "fieldtype": "Link",
            "options": "User",
            "width": "100px"
        },
        {
            "fieldname": "filter_based_on",
            "label": __("Filter Based On"),
            "fieldtype": "Select",
            "options": "modified|Last Modified\ncreation|Creation Date\nstart_date|Start Date\nend_date|Due Date",
            "default": "modified",
            "width": "100px"
        },
        {
            "fieldname": "time_interval",
            "label": __("Time Interval"),
            "fieldtype": "Select",
            "options": "\ntoday\nyesterday\nthis_week\nlast_week\nthis_month\nlast_month\nthis_quarter\nlast_quarter\nthis_year\nlast_year\nall",
            "default": "this_week",
            "width": "100px"
        },
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "width": "80px",
            "depends_on": "eval:doc.time_interval==''"
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "width": "80px",
            "depends_on": "eval:doc.time_interval==''"
        },
        {
            "fieldname": "show_backlogs",
            "label": __("Show Backlogs"),
            "fieldtype": "Check",
            "default": 1
        }
    ],
    
    "onload": function(report) {
        update_date_range(report);
        
        report.page.fields_dict.time_interval.$input.on("change", function() {
            update_date_range(report);
            report.refresh();
        });
        
        report.page.add_inner_button(__('Reset Filters'), function() {
            report.clear_filter_values();
            report.set_filter_value('time_interval', 'this_week');
            update_date_range(report);
            report.refresh();
        });
        
        report.page.add_inner_button(__('Today'), function() {
            report.set_filter_value('time_interval', 'today');
            update_date_range(report);
            report.refresh();
        }, __("Quick Filters"));
        
        report.page.add_inner_button(__('This Week'), function() {
            report.set_filter_value('time_interval', 'this_week');
            update_date_range(report);
            report.refresh();
        }, __("Quick Filters"));
        
        report.page.add_inner_button(__('Last Week'), function() {
            report.set_filter_value('time_interval', 'last_week');
            update_date_range(report);
            report.refresh();
        }, __("Quick Filters"));
        
        report.page.add_inner_button(__('This Month'), function() {
            report.set_filter_value('time_interval', 'this_month');
            update_date_range(report);
            report.refresh();
        }, __("Quick Filters"));
        
        report.page.add_inner_button(__('Export PDF'), function() {
            frappe.call({
                method: "frappe.desk.reportview.export_query",
                args: {
                    title: "Daily Weekly Progress Report",
                    filters: report.get_values(),
                    report_name: "Daily Weekly Progress Report",
                    file_format_type: "PDF"
                },
                callback: function(r) {
                    if (r.message) {
                        window.open('/api/method/frappe.utils.print_format.download_pdf?file_url=' + encodeURIComponent(r.message));
                    }
                }
            });
        }, __("Export"));
        
        report.page.add_inner_button(__('Export Excel'), function() {
            frappe.call({
                method: "frappe.desk.reportview.export_query",
                args: {
                    title: "Daily Weekly Progress Report",
                    filters: report.get_values(),
                    report_name: "Daily Weekly Progress Report",
                    file_format_type: "Excel"
                },
                callback: function(r) {
                    if (r.message) {
                        window.location.href = '/api/method/frappe.utils.file_manager.download_file?file_url=' + encodeURIComponent(r.message);
                    }
                }
            });
        }, __("Export"));
    },
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (!data) return value;
        
        if (column.fieldname == "progress_" && data.progress_ !== undefined && data.progress_ !== null) {
            let progress = data.progress_;
            if (progress < 30) {
                value = `<span style="color: #ff5858">${progress}%</span>`;
            } else if (progress < 70) {
                value = `<span style="color: #ffa00a">${progress}%</span>`;
            } else {
                value = `<span style="color: #28a745">${progress}%</span>`;
            }
        }
        
        if (column.fieldname == "days_left" && data.days_left) {
            if (data.days_left.includes("overdue")) {
                value = `<span style="color: #ff5858; font-weight: bold;">${data.days_left}</span>`;
            } else if (data.days_left.includes("today")) {
                value = `<span style="color: #ffa00a; font-weight: bold;">${data.days_left}</span>`;
            } else {
                value = `<span style="color: #28a745">${data.days_left}</span>`;
            }
        }
        
        if (column.fieldname == "status_display" && data.status_display) {
            if (data.status_display.includes("🟢")) {
                value = `<span style="color: #28a745; font-weight: bold;">${data.status_display}</span>`;
            } else if (data.status_display.includes("🟡")) {
                value = `<span style="color: #ffa00a; font-weight: bold;">${data.status_display}</span>`;
            } else if (data.status_display.includes("🔴")) {
                value = `<span style="color: #ff5858; font-weight: bold;">${data.status_display}</span>`;
            } else if (data.status_display.includes("⚫")) {
                value = `<span style="color: #6c757d; font-weight: bold;">${data.status_display}</span>`;
            } else if (data.status_display.includes("🟠")) {
                value = `<span style="color: #fd7e14; font-weight: bold;">${data.status_display}</span>`;
            } else {
                value = `<span style="color: #6c757d;">${data.status_display}</span>`;
            }
        }
        
        if (column.fieldname == "priority" && data.priority) {
            let priority = data.priority;
            let color = "";
            
            if (priority === "Critical") {
                color = "#ff5858";
            } else if (priority === "High") {
                color = "#ffa00a";
            } else if (priority === "Medium") {
                color = "#5e64ff";
            } else {
                color = "#28a745";
            }
            
            value = `<span style="color: ${color}; font-weight: bold;">${priority}</span>`;
        }
        
        if (column.fieldname == "task_name") {
            if (data.is_backlog === 1) {
                value = `<div style="background-color: rgba(255, 88, 88, 0.1); padding: 2px 5px; border-radius: 3px;">
                    <span style="color: #ff5858; font-weight: bold;">⚠️ </span>${value}
                </div>`;
            } else if (data.end_date && frappe.datetime.get_diff(data.end_date, frappe.datetime.get_today()) < 0 && 
                      data.status !== "Completed" && data.status !== "Cancelled") {
                value = `<div style="background-color: rgba(255, 88, 88, 0.1); padding: 2px 5px; border-radius: 3px;">
                    <span style="color: #ff5858; font-weight: bold;">⚠️ </span>${value}
                </div>`;
            }
        }

        if (column.fieldname == "time_spent" && data.time_spent) {
            value = `<span style="color: #7a3db8;">${data.time_spent}</span>`;
        }
        
        return value;
    }
};

function update_date_range(report) {
    var time_interval = report.get_filter_value('time_interval') || 'this_week';
    var today = frappe.datetime.get_today();
    var from_date, to_date;
    
    switch(time_interval) {
        case 'today':
            from_date = today;
            to_date = today;
            break;
        case 'yesterday':
            from_date = frappe.datetime.add_days(today, -1);
            to_date = frappe.datetime.add_days(today, -1);
            break;
        case 'this_week':
            from_date = frappe.datetime.week_start();
            to_date = frappe.datetime.week_end();
            break;
        case 'last_week':
            from_date = frappe.datetime.add_days(frappe.datetime.week_start(), -7);
            to_date = frappe.datetime.add_days(frappe.datetime.week_end(), -7);
            break;
        case 'this_month':
            from_date = frappe.datetime.month_start();
            to_date = frappe.datetime.month_end();
            break;
        case 'last_month':
            from_date = frappe.datetime.add_months(frappe.datetime.month_start(), -1);
            to_date = frappe.datetime.add_months(frappe.datetime.month_end(), -1);
            break;
        case 'this_quarter':
            from_date = frappe.datetime.quarter_start();
            to_date = frappe.datetime.quarter_end();
            break;
        case 'last_quarter':
            from_date = frappe.datetime.add_months(frappe.datetime.quarter_start(), -3);
            to_date = frappe.datetime.add_months(frappe.datetime.quarter_end(), -3);
            break;
        case 'this_year':
            from_date = frappe.datetime.year_start();
            to_date = frappe.datetime.year_end();
            break;
        case 'last_year':
            from_date = frappe.datetime.add_years(frappe.datetime.year_start(), -1);
            to_date = frappe.datetime.add_years(frappe.datetime.year_end(), -1);
            break;
        case 'all':
            from_date = '2000-01-01';
            to_date = frappe.datetime.get_today();
            break;
        default:
            // Default to this week if not specified
            from_date = frappe.datetime.week_start();
            to_date = frappe.datetime.week_end();
    }
    
    report.set_filter_value('from_date', from_date);
    report.set_filter_value('to_date', to_date);
}
