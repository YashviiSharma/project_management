// Copyright (c) 2025, Aman and Yashvi and contributors
// For license information, please see license.txt

frappe.query_reports["Member Timelogs"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1
        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project"
        }
    ],

    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname == "efficiency" && data && data.efficiency) {
            let efficiency = data.efficiency;
            let color = "red";
            
            if (efficiency >= 75) color = "green";
            else if (efficiency >= 50) color = "orange";
            
            value = `<span class="indicator ${color}">${value}</span>`;
        }
        
        if (column.fieldname == "last_active" && data && data.last_active) {
            value = frappe.datetime.str_to_user(value);
        }
        
        return value;
    },

    "onload": function(report) {
        report.page.add_inner_button(__('Reset Filters'), function() {
            report.clear_filter_values();
            report.refresh();
        });
    
        report.chart_options = {
            tooltipOptions: {
                formatTooltipX: function(d) {
                    return d;
                },
                formatTooltipY: function(d, i, j) {
                    if (j === 0) {
                        return d + " hours";  // Show hours in the chart tooltip
                    } else {
                        return d + " tasks";
                    }
                }
            }
        };
    }
};