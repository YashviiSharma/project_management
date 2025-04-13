// Copyright (c) 2025, Aman and Yashvi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project', {
    refresh: function(frm) {
        setupTaskButton(frm);
        setupDeliverableButton(frm);
        setupChannelButton(frm);
    }
});

function setupChannelButton(frm) {
    if (frm.doc.raven_channel) {
        frm.add_custom_button(__('Open Channel'), function() {
            frappe.call({
                method: 'frappe.client.get_value',
                args: {
                    doctype: 'Raven Channel',
                    filters: {name: frm.doc.raven_channel},
                    fieldname: 'name'
                },
                callback: function(response) {
                    if (response.message) {
                        const workspace_name = frm.doc.raven_channel.split('-')[0];
                        window.open(`/raven/${encodeURIComponent(workspace_name)}/${encodeURIComponent(frm.doc.raven_channel)}`, '_blank');
                    } else {
                        frappe.msgprint(__('Channel not found'), __('Error'));
                    }
                }
            });
        },);
    }
}

function setupTaskButton(frm) {
    frm.add_custom_button(__('Add Task'), () => showAddTaskDialog(frm));
}

function setupDeliverableButton(frm) {
    frm.add_custom_button(__('Add Deliverable'), () => checkProjectTasks(frm));
}

function showAddTaskDialog(frm) {
    getProjectTeamMembers(frm, teamMembers => {
        const defaultStartDate = getDefaultStartDate(frm);
        const defaultEndDate = getDefaultEndDate(frm);
        
        const taskDialog = new frappe.ui.Dialog({
            title: __('Add Task to Project'),
            fields: getTaskDialogFields(defaultStartDate, defaultEndDate, teamMembers),
            primary_action_label: __('Create Task'),
            primary_action: () => handleCreateTask(frm, taskDialog)
        });
        
        taskDialog.show();
    });
}

function getDefaultStartDate(frm) {
    const today = frappe.datetime.nowdate();
    if (frm.doc.start_date && frappe.datetime.str_to_obj(frm.doc.start_date) > frappe.datetime.str_to_obj(today)) {
        return frm.doc.start_date;
    }
    return today;
}

function getDefaultEndDate(frm) {
    if (!frm.doc.end_date) return '';
    
    const projectEnd = frappe.datetime.str_to_obj(frm.doc.end_date);
    projectEnd.setDate(projectEnd.getDate() - 1);
    return frappe.datetime.obj_to_str(projectEnd);
}

function getTaskDialogFields(defaultStartDate, defaultEndDate, teamMembers) {
    return [
        {
            label: __('Task Name'),
            fieldname: 'task_name',
            fieldtype: 'Data',
            reqd: 1,
            description: __('Enter a clear name that describes the task')
        },
        {
            label: __('Start Date'),
            fieldname: 'start_date',
            fieldtype: 'Date',
            default: defaultStartDate,
            description: __(`Date when work on this task should begin after ${defaultStartDate}`)
        },
        {
            label: __('End Date'),
            fieldname: 'end_date',
            fieldtype: 'Date',
            default: defaultEndDate,
            description: __(`Expected completion date for this task should be before ${defaultEndDate}`)
        },
        {
            label: __('Assignee'),
            fieldname: 'assigned_to',
            fieldtype: 'Select',
            options: teamMembers,
            description: __('Team member responsible for completing this task')
        },
        {
            label: __('Description'),
            fieldname: 'description',
            fieldtype: 'Small Text'
        }
    ];
}

function handleCreateTask(frm, taskDialog) {
    const values = taskDialog.get_values();
    
    if (!isValidTaskDates(frm, values)) {
        return;
    }
    
    createTask(frm, values, taskDialog);
}

function isValidTaskDates(frm, values) {
    // Check start date not before project start date
    if (frm.doc.start_date && values.start_date && 
        frappe.datetime.str_to_obj(values.start_date) < frappe.datetime.str_to_obj(frm.doc.start_date)) {
        frappe.msgprint(__("Task start date cannot be before project start date '{0}'", [frm.doc.start_date]));
        return false;
    }
    
    // Check end date not after project end date
    if (frm.doc.end_date && values.end_date && 
        frappe.datetime.str_to_obj(values.end_date) > frappe.datetime.str_to_obj(frm.doc.end_date)) {
        frappe.msgprint(__("Task end date cannot be after project end date '{0}'", [frm.doc.end_date]));
        return false;
    }
    
    return true;
}

function createTask(frm, values, taskDialog) {
    frappe.call({
        method: 'frappe.client.insert',
        args: {
            doc: {
                doctype: 'Task',
                task_name: values.task_name,
                project: frm.doc.name,
                start_date: values.start_date,
                end_date: values.end_date,
                assigned_to: values.assigned_to,
                description: values.description,
                priority: 'Medium',
                status: 'Planned',
                progress_: 0,
                time_in_hours: 0
            }
        },
        callback: response => {
            if(response.exc) return;
            
            showSuccessMessage(`Task "${values.task_name}" created successfully`);
            showPostCreationOptions(frm, taskDialog);
        }
    });
}

function showSuccessMessage(message) {
    frappe.show_alert({
        message: __(message),
        indicator: 'green'
    }, 3);
}

function showPostCreationOptions(frm, taskDialog) {
    taskDialog.hide();
    
    const options = [
        {
            label: __('Add Another Task'),
            action: () => {
                optionsDialog.hide();
                showAddTaskDialog(frm);
            },
            isPrimary: true
        },
        {
            label: __('Go To Task List'),
            action: () => {
                optionsDialog.hide();
                frappe.set_route('List', 'Task', {project: frm.doc.name});
            }
        },
        {
            label: __('View Task'),
            action: () => {
                optionsDialog.hide();
                frappe.set_route('Form', 'Task', taskDialog.get_values().task_name);
            }
        }
    ];
    
    const optionsDialog = createOptionsDialog('Task Created Successfully', options);
    optionsDialog.show();
}

function createOptionsDialog(title, options) {
    const dialog = new frappe.ui.Dialog({
        title: __(title),
        fields: [
            {
                fieldname: 'action_html',
                fieldtype: 'HTML',
                options: `<div class="text-center">
                    <p>${__('What would you like to do next?')}</p>
                </div>`
            }
        ]
    });
    
    options.forEach(option => {
        if (option.isPrimary) {
            dialog.set_primary_action(option.label, option.action);
        } else {
            dialog.add_custom_action(option.label, option.action, 'btn-info');
        }
    });
    
    return dialog;
}

function getProjectTeamMembers(frm, callback) {
    if (!frm.doc.team_member || frm.doc.team_member.length === 0) {
        callback([]);
        return;
    }
    
    const userList = frm.doc.team_member.map(member => member.user);
    
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'User',
            filters: { 'name': ['in', userList] },
            fields: ['name', 'full_name']
        },
        callback: response => {
            if (!response.message || response.message.length === 0) {
                callback([]);
                return;
            }
            
            const teamMembers = response.message.map(user => ({
                value: user.name,
                label: user.full_name || user.name
            }));
            
            callback(teamMembers);
        }
    });
}

function checkProjectTasks(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Task',
            filters: { 'project': frm.doc.name },
            limit_page_length: 1
        },
        callback: response => {
            if (!response.message || response.message.length === 0) {
                showNoTasksDialog(frm);
                return;
            }
            
            showAddDeliverableDialog(frm);
        }
    });
}

function showNoTasksDialog(frm) {
    const options = [
        {
            label: __('Add Task First'),
            action: () => {
                noTasksDialog.hide();
                showAddTaskDialog(frm);
            },
            isPrimary: true
        },
        {
            label: __('Continue Adding Deliverable'),
            action: () => {
                noTasksDialog.hide();
                showAddDeliverableDialog(frm);
            }
        }
    ];
    
    const messageHtml = `<div class="text-center">
        <p>${__('No tasks have been linked to this project yet.')}</p>
        <p>${__('It is recommended to add tasks first before creating deliverables.')}</p>
        <p>${__('What would you like to do?')}</p>
    </div>`;
    
    const noTasksDialog = createCustomDialog(
        __('No Tasks Found Linked to Project {0}', [frm.doc.project_name]), 
        messageHtml,
        options
    );
    
    noTasksDialog.show();
}

function createCustomDialog(title, messageHtml, options) {
    const dialog = new frappe.ui.Dialog({
        title: __(title),
        fields: [
            {
                fieldname: 'message_html',
                fieldtype: 'HTML',
                options: messageHtml
            }
        ]
    });
    
    options.forEach(option => {
        if (option.isPrimary) {
            dialog.set_primary_action(option.label, option.action);
        } else {
            dialog.add_custom_action(option.label, option.action, option.btnClass || 'btn-default');
        }
    });
    
    return dialog;
}

function showAddDeliverableDialog(frm) {
    getProjectTasks(frm, tasks => {
        const deliverableDialog = new frappe.ui.Dialog({
            title: __('Add Deliverable'),
            fields: getDeliverableDialogFields(frm, tasks),
            primary_action_label: __('Create'),
            primary_action: () => handleCreateDeliverable(frm, deliverableDialog)
        });
        
        deliverableDialog.show();
    });
}

function getProjectTasks(frm, callback) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Task',
            filters: { 'project': frm.doc.name },
            fields: ['name', 'task_name', 'assigned_to']
        },
        callback: response => {
            if (!response.message) {
                callback([]);
                return;
            }
            
            const tasks = response.message.map(task => ({
                value: task.name,
                label: `${task.task_name}${task.assigned_to ? 
                    ` (Assigned to: ${task.assigned_to})` : ' (Yet to be assigned)'}`
            }));
            
            callback(tasks);
        }
    });
}

function getDeliverableDialogFields(frm, tasks) {
    return [
        {
            label: __('Deliverable Name'),
            fieldname: 'deliverable_name',
            fieldtype: 'Data',
            reqd: 1
        },
        {
            label: __('Due Date'),
            fieldname: 'due_date',
            fieldtype: 'Date',
            reqd: 1,
            description: __(`Must be between ${frm.doc.start_date} and ${frm.doc.end_date}`)
        },
        {
            label: __('Linked Tasks'),
            fieldname: 'linked_tasks',
            fieldtype: 'MultiSelect',
            options: tasks,
            description: __(`You can link multiple tasks to this deliverable. Select tasks from the list.`)
        },
        {
            label: __('Description'),
            fieldname: 'description',
            fieldtype: 'Small Text'
        }
    ];
}

function handleCreateDeliverable(frm, deliverableDialog) {
    const values = deliverableDialog.get_values();
    
    if (!isValidDeliverableDate(frm, values)) {
        return;
    }
    
    createDeliverable(frm, values, deliverableDialog);
}

function isValidDeliverableDate(frm, values) {
    const dueDate = frappe.datetime.str_to_obj(values.due_date);
    const projectStart = frappe.datetime.str_to_obj(frm.doc.start_date);
    const projectEnd = frappe.datetime.str_to_obj(frm.doc.end_date);

    if (dueDate < projectStart || dueDate > projectEnd) {
        frappe.msgprint(__(`Due date must be in between project start date '${frm.doc.start_date}' and end date '${frm.doc.end_date}'`));
        return false;
    }
    
    return true;
}

function createDeliverable(frm, values, deliverableDialog) {
    frappe.call({
        method: 'frappe.client.insert',
        args: {
            doc: {
                doctype: 'Deliverable',
                deliverable_name: values.deliverable_name,
                project: frm.doc.name,
                due_date: values.due_date,
                priority: 'Medium',
                // status: 'In Progress',
                description_for_this_deliverable: values.description
            }
        },
        callback: response => {
            if (response.exc) {
                frappe.msgprint(__('Failed to create deliverable: ') + response.exc);
                return;
            }
            
            const deliverable = response.message;
            
            if (!values.linked_tasks) {
                handleDeliverableCreationSuccess(frm, deliverableDialog, deliverable.name);
                return;
            }
            
            processDeliverableTasks(frm, values, deliverable, deliverableDialog);
        }
    });
}

function processDeliverableTasks(frm, values, deliverable, deliverableDialog) {
    const selectedTasks = values.linked_tasks.split(',').map(task => task.trim());
    const taskEndDate = frappe.datetime.add_days(values.due_date, -1);
    let successCount = 0;
    let errorMessages = [];
    
    const processNextTask = async (index) => {
        if (index >= selectedTasks.length) {
            completeDeliverableCreation(
                frm, 
                deliverableDialog, 
                deliverable, 
                values, 
                successCount, 
                selectedTasks.length, 
                errorMessages
            );
            return;
        }
        
        const taskName = selectedTasks[index];
        try {
            await updateTaskEndDate(taskName, taskEndDate, errorMessages);
            await linkTaskToDeliverable(taskName, deliverable.name, errorMessages);
            successCount++;
        } catch (error) {
            // Error already added to errorMessages
        }
        
        processNextTask(index + 1);
    };
    
    processNextTask(0);
}

async function updateTaskEndDate(taskName, taskEndDate, errorMessages) {
    const result = await frappe.call({
        method: 'frappe.client.set_value',
        args: {
            doctype: 'Task',
            name: taskName,
            fieldname: 'end_date',
            value: taskEndDate
        }
    });
    
    if (result.exc) {
        errorMessages.push(__('Task {0}: {1}', [taskName, result.exc]));
        throw result.exc;
    }
    
    return result;
}

async function linkTaskToDeliverable(taskName, deliverableName, errorMessages) {
    const result = await frappe.call({
        method: 'frappe.client.insert',
        args: {
            doc: {
                doctype: 'Deliverable Task',
                parent: deliverableName,
                parenttype: 'Deliverable',
                parentfield: 'tasks',
                task: taskName
            }
        }
    });
    
    if (result.exc) {
        errorMessages.push(__('Task {0}: {1}', [taskName, result.exc]));
        throw result.exc;
    }
    
    return result;
}

function completeDeliverableCreation(frm, dialog, deliverable, values, successCount, totalTasks, errorMessages) {
    let message = __(`Deliverable '${values.deliverable_name}' created successfully`);
    let indicator = 'green';
    
    if (successCount > 0) {
        message += `<br>${successCount}/${totalTasks} tasks end date updated successfully`;
    }
    
    if (errorMessages.length > 0) {
        message += `<br>Errors:<br>- ${errorMessages.join('<br>- ')}`;
        indicator = 'orange';
    }
    
    frappe.show_alert({ message, indicator }, 8);
    
    frm.reload_doc();
    dialog.hide();
    
    showPostDeliverableCreationOptions(frm, deliverable.name);
}

function handleDeliverableCreationSuccess(frm, dialog, deliverableName) {
    showSuccessMessage('Deliverable created successfully');
    dialog.hide();
    frm.reload_doc();
    
    showPostDeliverableCreationOptions(frm, deliverableName);
}

function showPostDeliverableCreationOptions(frm, deliverableName) {
    const options = [
        {
            label: __('Add Another Deliverable'),
            action: () => {
                optionsDialog.hide();
                showAddDeliverableDialog(frm);
            },
            isPrimary: true
        },
        {
            label: __('Go To Deliverable List'),
            action: () => {
                optionsDialog.hide();
                frappe.set_route('List', 'Deliverable', {project: frm.doc.name});
            }
        },
        {
            label: __('View Deliverable'),
            action: () => {
                optionsDialog.hide();
                frappe.set_route('Form', 'Deliverable', deliverableName);
            }
        }
    ];
    
    const optionsDialog = createOptionsDialog('Deliverable Created Successfully', options);
    optionsDialog.show();
}