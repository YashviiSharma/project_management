// Copyright (c) 2025, Aman and Yashvi and contributors
// For license information, please see license.txt

frappe.query_reports["Resource Allocation"] = {
    "filters": [
        {
            "fieldname": "team_member",
            "label": __("Team Member"),
            "fieldtype": "Link",
            "options": "User",
            "reqd": 0
        },
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "Link",
            "options": "Project",
            "reqd": 0
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": ["", "Planned", "In Progress", "On Hold", "Completed", "Cancelled"],
            "reqd": 0
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        if (column.fieldname == "status") {
            if (data.status == "Completed") {
                value = `<span style="color:green;">${value}</span>`;
            } else if (data.status == "Cancelled") {
                value = `<span style="color:red;">${value}</span>`;
            } else if (data.status == "In Progress") {
                value = `<span style="color:blue;">${value}</span>`;
            } else if (data.status == "On Hold") {
                value = `<span style="color:orange;">${value}</span>`;
            }
        }
        
        if (column.fieldname == "priority") {
            if (data.priority == "Critical" || data.priority == "High") {
                value = `<span style="color:red;font-weight:bold;">${value}</span>`;
            } else if (data.priority == "Medium") {
                value = `<span style="color:orange;">${value}</span>`;
            }
        }
        
        return value;
    },
    
    "onload": function(report) {
        report.page.add_inner_button(__("Export as Excel"), function() {
            var filters = report.get_values();
            frappe.call({
                method: "frappe.core.doctype.data_export.exporter.export_data",
                args: {
                    doctype: "Resource Allocation",
                    file_format_type: "Excel",
                    filters: filters
                },
                callback: function(r) {
                    if(r.message) {
                        var doc = frappe.model.sync(r.message)[0];
                        frappe.set_route("Form", doc.doctype, doc.name);
                    }
                }
            });
        });
    },
    
    "get_chart_data": function(_columns, result) {
        let labels = [];
        let project_data = {};
        let status_data = {};
        
        result.forEach(row => {
            if (row.project && !labels.includes(row.project)) {
                labels.push(row.project);
            }
            
            if (row.project) {
                project_data[row.project] = (project_data[row.project] || 0) + 1;
            }
            
            if (row.status) {
                status_data[row.status] = (status_data[row.status] || 0) + 1;
            }
        });
        
        let datasets = [
            {
                name: "Projects/Tasks Count",
                chartType: "bar",
                values: labels.map(label => project_data[label] || 0)
            },
            {
                name: "Completed",
                chartType: "line",
                values: labels.map(label => {
                    return result.filter(row => row.project === label && row.status === "Completed").length;
                })
            },
            {
                name: "In Progress",
                chartType: "line",
                values: labels.map(label => {
                    return result.filter(row => row.project === label && row.status === "In Progress").length;
                })
            }
        ];
        
        return {
            data: {
                labels: labels,
                datasets: datasets
            },
            type: "axis-mixed",
            height: 300,
            colors: ["#7CD6FD", "#743EE2", "#FF5858"],
            barOptions: {
                spaceRatio: 0.2
            },
            axisOptions: {
                xIsSeries: true
            },
            tooltipOptions: {
                formatTooltipX: d => (d + '').toUpperCase(),
                formatTooltipY: d => d + (d > 1 ? " items" : " item")
            }
        };
    }
};