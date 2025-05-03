// Copyright (c) 2025, Aman and Yashvi and contributors
// For license information, please see license.txt

frappe.query_reports["Task Status"] = {
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
		"fieldname": "from_date",
		"label": __("From Start Date"),
		"fieldtype": "Date",
		"default": frappe.datetime.add_months(frappe.datetime.get_today(), -3)
	  },
	  {
		"fieldname": "to_date",
		"label": __("To End Date"),
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
	  // Initialize report with default settings
	  report.page.add_inner_button(__('Reset Filters'), function() {
		report.clear_filter_values();
		report.refresh();
	  });
	  
	  // Add a button to link to Deliverable Status report
	  report.page.add_inner_button(__('View Deliverables'), function() {
		frappe.set_route('query-report', 'Deliverable Status');
	  });
	  
	  // Format the Progress column to show visual progress bar
	  report.formatter = function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		
		if (column.fieldname == "progress_" && data && data.progress_) {
		  let progress_ = data.progress_;
		  let color = "green";
		  
		  if (progress_ < 30) color = "red";
		  else if (progress_ < 70) color = "orange";
		  
		  value = `<div class="progress" style="height: 16px; margin-bottom: 0;">
				  <div class="progress-bar bg-${color}" role="progressbar" 
					 style="width: ${progress_}%" aria-valuenow="${progress_}" 
					 aria-valuemin="0" aria-valuemax="100">
					${progress_}%
				  </div>
				</div>`;
		}
		
		// Format days left with colors
		if (column.fieldname == "days_left" && data) {
		  let days = data.days_left;
		  
		  if (days !== null) {
			if (days < 0) {
			  value = `<span style="color: red; font-weight: bold;">${days}</span>`;
			} else if (days <= 2) {
			  value = `<span style="color: orange; font-weight: bold;">${days}</span>`;
			} else {
			  value = `<span style="color: green;">${days}</span>`;
			}
		  }
		}
		
		// Format status with colors
		if (column.fieldname == "status" && data && data.status) {
		  let status = data.status;
		  let color = "";
		  
		  if (status === "Completed") color = "green";
		  else if (status === "In Progress") color = "blue";
		  else if (status === "On Hold" || status === "Paused") color = "orange";
		  else if (status === "Cancelled") color = "red";
		  else color = "purple"; // Planned
		  
		  value = `<span class="indicator ${color}">${status}</span>`;
		}
		
		// Format priority with colors
		if (column.fieldname == "priority" && data && data.priority) {
		  let priority = data.priority;
		  let color = "";
		  
		  if (priority === "Critical") color = "red";
		  else if (priority === "High") color = "orange";
		  else if (priority === "Medium") color = "blue";
		  else color = "green"; // Low
		  
		  value = `<span class="indicator ${color}">${priority}</span>`;
		}
		
		// Format datetime fields for better readability
		if ((column.fieldname == "actual_start" || column.fieldname == "actual_end") && data) {
		  let datetime = data[column.fieldname];
		  if (datetime) {
			// Format the datetime for better readability
			try {
			  let formattedDate = frappe.datetime.str_to_user(datetime);
			  value = formattedDate;
			} catch (e) {
			  // If any error in formatting, use the original value
			  console.error("Error formatting datetime:", e);
			}
		  }
		}
		
		return value;
	  };
	  
	  // Add a callback after report is run
	  report.page.wrapper.on('render-complete', function() {
		// You could add custom behaviors here after the report renders
		console.log("Task Status Report rendered successfully");
	  });
	}
  };