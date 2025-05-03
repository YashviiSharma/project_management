// Copyright (c) 2025, Aman and Yashvi and contributors
// For license information, please see license.txt

frappe.query_reports["Deliverable Status"] = {
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
			"options": "\nIn Progress\nAwaiting Client Review\nRequired Changes\nApproved\nRejected",
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
			"fieldname": "from_date",
			"label": __("From Due Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), -3)
		},
		{
			"fieldname": "to_date",
			"label": __("To Due Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_months(frappe.datetime.get_today(), 3)
		},
		{
			"fieldname": "overdue",
			"label": __("Show Overdue"),
			"fieldtype": "Check"
		}
	],
	
	"onload": function(report) {
		report.page.add_inner_button(__('Reset Filters'), function() {
			report.clear_filter_values();
			report.refresh();
		});
		
		report.page.wrapper.on('render-complete', function() {
			console.log("Report rendered successfully");
		});
	}
};