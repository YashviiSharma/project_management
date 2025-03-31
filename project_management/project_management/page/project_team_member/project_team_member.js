frappe.pages['project-team-member'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Project Team Member Dashboard',
        single_column: true
    });

    let content = $(`
        <style>
            .dashboard-container {
                padding: 20px;
                background-color: #f8f9fa;
                border-radius: 10px;
            }
            .dashboard-header {
                text-align: center;
                padding: 10px;
                font-size: 24px;
                font-weight: bold;
                background-color: #007bff;
                color: white;
                border-radius: 5px;
            }
            .dashboard-section {
                margin-top: 20px;
                padding: 15px;
                background: white;
                border-radius: 8px;
                box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
            }
            .chart-container {
                width: 100%;
                height: 300px;
            }
            .task-list {
                list-style: none;
                padding: 0;
            }
            .task-item {
                display: flex;
                justify-content: space-between;
                padding: 8px;
                border-bottom: 1px solid #ddd;
            }
            .task-status {
                padding: 5px;
                border-radius: 5px;
            }
            .time-tracking-table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                border-radius: 8px;
                overflow: hidden;
                background: white;
                box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
            }

            .time-tracking-table th, .time-tracking-table td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }

            .time-tracking-table th {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                text-transform: uppercase;
            }

            .time-tracking-table tr:nth-child(even) {
                 background-color: #f8f9fa;
            }

            .no-logs {
                text-align: center;
                padding: 10px;
                color: #777;
                font-style: italic;
            }
            #personal-task-list {
                display: flex;
                flex-direction: column;
                gap: 10px;
                padding: 10px;
            }

            .task-card {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px;
                background: #e3f2fd; /* Light Blue Theme */
                border-radius: 10px;
                box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
                transition: transform 0.2s ease-in-out, background 0.2s;
            }

            .task-card:hover {
                transform: scale(1.03);
                background: #bbdefb; /* Darker blue on hover */
            }

            .task-info {
                display: flex;
                align-items: center;
                font-size: 16px;
                font-weight: 600;
                color: #1565c0;
            }

            .task-actions {
                display: flex;
                align-items: center;
            }

            .task-actions .delete-task-btn {
                background: transparent;
                border: none;
                font-size: 20px;
                cursor: pointer;
                transition: transform 0.2s;
            }

            .task-actions .delete-task-btn:hover {
                transform: scale(1.2);
            }

            .no-tasks {
                text-align: center;
                font-size: 14px;
                color: #777;
                padding: 10px;
                font-style: italic;
            }


        </style>

        <div class="dashboard-container">
            <div class="dashboard-header">
                <h2>Project Team Member Dashboard</h2>
            </div>
            <div class="dashboard-section">
                <h3>Task Status Overview</h3>
                <div id="task-status-chart" class="chart-container"></div>
            </div>
            <div class="dashboard-section">
                <h3>Personal Task List</h3>
                <ul id="personal-task-list" class="task-list"></ul>
            </div>
            <div class="dashboard-section">
                <h3>Task Progress</h3>
                <div id="task-progress-chart" class="chart-container"></div>
            </div>

            <div class="dashboard-section">
                <h3>Assigned Tasks</h3>
                <ul id="task-list" class="task-list"></ul>
            </div>
            <div class="dashboard-section">
                <h3>Time Tracking</h3>
                <ul id="time-logs" class="task-list"></ul>
            </div>
        </div>
    `);

    content.appendTo(page.body);  

    setTimeout(() => {
        loadTaskStatusChart();
        loadTaskProgressChart();
    }, 500); 

    loadTimeTracking();
    loadAssignedTasks();
    loadPersonalTasks();
};

function loadTimeTracking() {
    frappe.call({
        method: "project_management.api.get_time_tracking",
        callback: function(response) {
            let timeLogs = response.message;
            let timeContainer = $("#time-logs");

            if (!timeLogs || timeLogs.length === 0) {
                timeContainer.html("<div class='no-logs'>No time logs available.</div>");
                return;
            }

            timeContainer.empty();

            let table = $(`
                <table class="time-tracking-table">
                    <thead>
                        <tr>
                            <th>Task Name</th>
                            <th>Total Hours Spent</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            `);

            timeLogs.forEach(log => {
                table.find("tbody").append(`
                    <tr>
                        <td>${log.task_name}</td>
                        <td>${log.time_in_hours} hrs</td>
                    </tr>
                `);
            });

            timeContainer.append(table);
        }
    });
}
function loadTaskStatusChart() {
    frappe.call({
        method: "project_management.api.get_task_status_chart",
        callback: function(response) {
            console.log("Task Status API Response:", response.message);
            new frappe.Chart("#task-status-chart", {
                data: response.message,
                type: 'pie',
                title: "Task Status Overview"
            });
        }
    });
}

function loadTaskProgressChart() {
    frappe.call({
        method: "project_management.api.get_task_progress_chart",
        callback: function(response) {
            console.log("Task Progress API Response:", response.message);
            let chartElement = document.getElementById("task-progress-chart");

            if (!chartElement) {
                console.error("Chart container #task-progress-chart not found!");
                return;
            }

            new frappe.Chart("#task-progress-chart", {
                data: response.message,
                type: 'bar',
                title: "Task Progress",
                colors: ['#34A853'], 
                axisOptions: {
                    xAxisMode: "tick",
                    yAxisMode: "span",
                    xIsSeries: true
                }
            });
        }
    });
}

function loadAssignedTasks() {
    frappe.call({
        method: "project_management.api.get_assigned_tasks",
        callback: function(response) {
            let tasks = response.message;
            console.log("Assigned Tasks API Response:", tasks);
            let taskContainer = $("#task-list");

            if (!tasks || tasks.length === 0) {
                taskContainer.html("<li>No tasks assigned.</li>");
                return;
            }

            taskContainer.empty();
            tasks.forEach(task => {
                let listItem = $(`
                    <li class="task-item">
                        <span>${task.task_name} - <strong>${task.status}</strong></span>
                        <select class="task-status" data-task="${task.name}">
                            <option value="Planned" ${task.status === "Planned" ? "selected" : ""}>Planned</option>
                            <option value="In Progress" ${task.status === "In Progress" ? "selected" : ""}>In Progress</option>
                            <option value="Completed" ${task.status === "Completed" ? "selected" : ""}>Completed</option>
                            <option value="On Hold" ${task.status === "On Hold" ? "selected" : ""}>On Hold</option>
                            <option value="Cancelled" ${task.status === "Cancelled" ? "selected" : ""}>Cancelled</option>
                        </select>
                    </li>
                `);

                listItem.find(".task-status").on("change", function() {
                    let taskId = $(this).data("task");
                    let newStatus = $(this).val();
                    updateTaskStatus(taskId, newStatus);
                });

                taskContainer.append(listItem);
            });
        }
    });
}

function updateTaskStatus(taskName, status) {
    frappe.call({
        method: "project_management.api.update_task_status",
        args: { task_name: taskName, status: status },
        callback: function (response) {
            if (response.message === "success") {
                frappe.msgprint(`✅ Task updated to "${status}"`);
                loadPersonalTasks();
                loadTaskProgressChart();  // Refresh the chart after status update
            } else {
                frappe.msgprint("❌ Error updating task.");
            }
        }
    });
}
function loadPersonalTasks() {
    frappe.call({
        method: "project_management.api.get_personal_tasks",
        callback: function(response) {
            let personalTasks = response.message;
            let personalTaskContainer = $("#personal-task-list");

            personalTaskContainer.empty(); // Clear existing list

            if (!personalTasks || personalTasks.length === 0) {
                personalTaskContainer.html(`<div class="no-tasks">🚀 No personal tasks available.</div>`);
                return;
            }

            personalTasks.forEach(task => {
                let taskItem = `
                    <div class="task-card">
                        <div class="task-info">
                            <span class="task-title">📌 ${task.task_name}</span>
                        </div>
                        <div class="task-actions">
                            <button class="delete-task-btn" data-task="${task.task_name}" title="Delete Task">
                                🗑️
                            </button>
                        </div>
                    </div>
                `;

                personalTaskContainer.append(taskItem);
            });

            // Attach event to delete buttons
            $(".delete-task-btn").click(function () {
                let taskName = $(this).data("task");
                deleteTask(taskName);
            });
        }
    });
}

function deleteTask(taskName) {
    frappe.confirm(
        `⚠️ Are you sure you want to delete "${taskName}"?`,
        function () {
            frappe.call({
                method: "project_management.api.delete_task",
                args: { task_name: taskName },
                callback: function (response) {
                    if (response.message === "success") {
                        frappe.msgprint("✅ Task deleted successfully!");
                        loadPersonalTasks(); 
                        loadTaskProgressChart();  // Refresh the chart after deletion
                    } else {
                        frappe.msgprint("❌ Error deleting task.");
                    }
                }
            });
        }
    );
}
