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
                <h3>Task Progress</h3>
                <div id="task-progress-chart" class="chart-container"></div>
            </div>

            <div class="dashboard-section">
                <h3>Assigned Tasks</h3>
                <ul id="task-list" class="task-list"></ul>
            </div>

            <div class="dashboard-section">
                <h3>Personal Task List</h3>
                <ul id="personal-task-list" class="task-list"></ul>
            </div>

            <div class="dashboard-section">
                <h3>Time Tracking</h3>
                <ul id="time-logs" class="task-list"></ul>
            </div>
        </div>
    `);

    content.appendTo(page.body);  // Append content before calling charts

    // ✅ Delay Chart Rendering Until HTML is Loaded
    setTimeout(() => {
        loadTaskStatusChart();
        loadTaskProgressChart();
    }, 500);  // 500ms delay to ensure HTML exists

    loadAssignedTasks();
    loadPersonalTasks();
    loadTimeTracking();
};

// ✅ Load Task Status Chart
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

// ✅ Load Task Progress Chart
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

// ✅ Load Assigned Tasks
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
                let listItem = `<li class="task-item">
                    <span>${task.task_name} - ${task.status}</span>
                    <select class="task-status" data-task="${task.name}">
                        <option value="Planned" ${task.status === "Planned" ? "selected" : ""}>Planned</option>
                        <option value="In Progress" ${task.status === "In Progress" ? "selected" : ""}>In Progress</option>
                        <option value="Completed" ${task.status === "Completed" ? "selected" : ""}>Completed</option>
                        <option value="On Hold" ${task.status === "On Hold" ? "selected" : ""}>On Hold</option>
                        <option value="Cancelled" ${task.status === "Cancelled" ? "selected" : ""}>Cancelled</option>
                    </select>
                </li>`;
                taskContainer.append(listItem);
            });
        }
    });
}

// ✅ Load Personal Tasks
function loadPersonalTasks() {
    frappe.call({
        method: "project_management.api.get_personal_tasks",
        callback: function(response) {
            let personalTasks = response.message;
            let personalTaskContainer = $("#personal-task-list");

            if (!personalTasks || personalTasks.length === 0) {
                personalTaskContainer.html("<li>No personal tasks available.</li>");
                return;
            }

            personalTaskContainer.empty();
            personalTasks.forEach(task => {
                personalTaskContainer.append(`<li>${task.task_name}</li>`);
            });
        }
    });
}

// ✅ Load Time Tracking
function loadTimeTracking() {
    frappe.call({
        method: "project_management.api.get_time_tracking",
        callback: function(response) {
            let timeLogs = response.message;
            let timeContainer = $("#time-logs");

            if (!timeLogs || timeLogs.length === 0) {
                timeContainer.html("<li>No time logs available.</li>");
                return;
            }

            timeContainer.empty();
            timeLogs.forEach(log => {
                timeContainer.append(`<li>${log.task_name} - ${log.time_in_hours} hrs</li>`);
            });
        }
    });
}
