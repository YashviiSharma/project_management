// Copyright (c) 2025, Aman and Yashvi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project', {
    refresh: function(frm) {
        // Add task and deliverable buttons
        setup_task_button(frm);
        setup_deliverable_button(frm);
    }
});

// Setup Add Task button
function setup_task_button(frm) {
    frm.add_custom_button(__('Add Task'), function() {
        show_add_task_dialog(frm);
    });
}

// Show dialog for adding a new task with simplified fields
function show_add_task_dialog(frm) {
    // Get team members for the project for assignee field
    get_project_team_members(frm, function(team_members) {
        // Set default start date (today or project start date, whichever is later)
        let default_start_date = frappe.datetime.nowdate();
        if (frm.doc.start_date && frappe.datetime.str_to_obj(frm.doc.start_date) > frappe.datetime.str_to_obj(default_start_date)) {
            default_start_date = frm.doc.start_date;
        }
        
        // Set default end date (one day before project end date)
        let default_end_date = '';
        if (frm.doc.end_date) {
            let project_end = frappe.datetime.str_to_obj(frm.doc.end_date);
            project_end.setDate(project_end.getDate() - 1);
            default_end_date = frappe.datetime.obj_to_str(project_end);
        }
        
        let task_dialog = new frappe.ui.Dialog({
            title: __('Add Task to Project'),
            fields: [
                {
                    label: __('Task Name'),
                    fieldname: 'task_name',
                    fieldtype: 'Data',
                    reqd: 1
                },
                {
                    label: __('Start Date'),
                    fieldname: 'start_date',
                    fieldtype: 'Date',
                    default: default_start_date
                },
                {
                    label: __('End Date'),
                    fieldname: 'end_date',
                    fieldtype: 'Date',
                    default: default_end_date
                },
                {
                    label: __('Assignee'),
                    fieldname: 'assigned_to',
                    fieldtype: 'Select',
                    options: team_members
                },
                {
                    label: __('Description'),
                    fieldname: 'description',
                    fieldtype: 'Small Text'
                }
            ],
            primary_action_label: __('Create Task'),
            primary_action: function() {
                let values = task_dialog.get_values();
                
                // Validate end date not after project end date
                if (frm.doc.end_date && values.end_date && frappe.datetime.str_to_obj(values.end_date) > frappe.datetime.str_to_obj(frm.doc.end_date)) {
                    frappe.msgprint(__("Task end date cannot be after project end date"));
                    return;
                }
                
                // Create new task with default values
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
                            priority: 'Medium', // Default priority
                            status: 'Planned',  // Default status
                            progress_: 0,       // Default progress
                            time_in_hours: 0    // Default time
                        }
                    },
                    callback: function(r) {
                        if(!r.exc) {
                            frappe.show_alert({
                                message: __("Task created successfully"),
                                indicator: 'green'
                            }, 3);
                            task_dialog.hide();
                        }
                    }
                });
            }
        });
        task_dialog.show();
    });
}

// Get team members for the project
function get_project_team_members(frm, callback) {
    let team_members = [];
    
    if (frm.doc.team_member && frm.doc.team_member.length > 0) {
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'User',
                filters: {
                    'name': ['in', frm.doc.team_member.map(member => member.user)]
                },
                fields: ['name', 'full_name']
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    team_members = r.message.map(user => ({
                        value: user.name,
                        label: user.full_name || user.name
                    }));
                }
                callback(team_members);
            }
        });
    } else {
        callback(team_members);
    }
}

// Setup Add Deliverable button
function setup_deliverable_button(frm) {
    frm.add_custom_button(__('Add Deliverable'), function() {
        show_add_deliverable_dialog(frm);
    });
}

// Show dialog for adding a new deliverable with simplified fields
function show_add_deliverable_dialog(frm) {
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Task',
            filters: { 'project': frm.doc.name },
            fields: ['name', 'task_name', 'assigned_to']
        },
        callback: function(r) {
            let tasks = r.message.map(task => ({
                value: task.name,
                label: `${task.task_name}${task.assigned_to ? ` (Assigned to: ${task.assigned_to})` : ' (Yet to be assigned)'}`
            }));

            let deliverable_dialog = new frappe.ui.Dialog({
                title: __('Add Deliverable'),
                fields: [
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
                        description: __('Must be between project dates')
                    },
                    {
                        label: __('Linked Tasks'),
                        fieldname: 'linked_tasks',
                        fieldtype: 'MultiSelect',
                        options: tasks,
                        reqd: 0
                    },
                    {
                        label: __('Description'),
                        fieldname: 'description',
                        fieldtype: 'Small Text'
                    }
                ],
                primary_action_label: __('Create'),
                primary_action: function() {
                    let values = deliverable_dialog.get_values();
                    
                    // Validate due date
                    let due_date = frappe.datetime.str_to_obj(values.due_date);
                    let project_start = frappe.datetime.str_to_obj(frm.doc.start_date);
                    let project_end = frappe.datetime.str_to_obj(frm.doc.end_date);

                    if (due_date < project_start || due_date > project_end) {
                        frappe.msgprint(__(`Due date must be between project dates ${frm.doc.start_date} and ${frm.doc.end_date}`));
                        return;
                    }                    

                    // Create Deliverable
                    frappe.call({
                        method: 'frappe.client.insert',
                        args: {
                            doc: {
                                doctype: 'Deliverable',
                                deliverable_name: values.deliverable_name,
                                project: frm.doc.name,
                                due_date: values.due_date,
                                priority: 'Medium',
                                status: 'Draft',
                                description_for_this_deliverable: values.description
                            }
                        },
                        callback: function(r) {
                            if (r.exc) {
                                frappe.msgprint(__('Failed to create deliverable: ') + r.exc);
                                return;
                            }
                            
                            let deliverable = r.message;
                            if (values.linked_tasks) {
                                let selected_tasks = values.linked_tasks.split(',')
                                    .map(task => task.trim());
                                
                                let task_end_date = frappe.datetime.add_days(values.due_date, -1);
                                let success_count = 0;
                                let error_messages = [];
                                
                                // Process tasks sequentially to avoid version conflicts
                                const processNextTask = async (index) => {
                                    if (index >= selected_tasks.length) {
                                        // Final completion
                                        let msg = __('Deliverable created successfully');
                                        if (success_count > 0) {
                                            msg += `<br>${success_count}/${selected_tasks.length} tasks updated successfully`;
                                        }
                                        if (error_messages.length > 0) {
                                            msg += `<br>Errors:<br>- ${error_messages.join('<br>- ')}`;
                                        }
                                        
                                        frappe.show_alert({
                                            message: msg,
                                            indicator: error_messages.length ? 'orange' : 'green'
                                        }, 8);
                                        
                                        frm.reload_doc();
                                        deliverable_dialog.hide();
                                        return;
                                    }
                                    
                                    const task_name = selected_tasks[index];
                                    try {
                                        // Update Task end_date
                                        const update_result = await frappe.call({
                                            method: 'frappe.client.set_value',
                                            args: {
                                                doctype: 'Task',
                                                name: task_name,
                                                fieldname: 'end_date',
                                                value: task_end_date
                                            }
                                        });
                                        
                                        if (update_result.exc) {
                                            error_messages.push(__('Task {0}: {1}', [task_name, update_result.exc]));
                                            throw update_result.exc;
                                        }
                                        
                                        // Link to deliverable
                                        const link_result = await frappe.call({
                                            method: 'frappe.client.insert',
                                            args: {
                                                doc: {
                                                    doctype: 'Deliverable Task',
                                                    parent: deliverable.name,
                                                    parenttype: 'Deliverable',
                                                    parentfield: 'tasks',
                                                    task: task_name
                                                }
                                            }
                                        });
                                        
                                        if (link_result.exc) {
                                            error_messages.push(__('Task {0}: {1}', [task_name, link_result.exc]));
                                            throw link_result.exc;
                                        }
                                        
                                        success_count++;
                                    } catch (error) {
                                        // Error already logged, continue processing
                                    }
                                    
                                    // Process next task
                                    processNextTask(index + 1);
                                };
                                
                                // Start processing
                                processNextTask(0);
                            } else {
                                frappe.show_alert({
                                    message: __('Deliverable created successfully'),
                                    indicator: 'green'
                                }, 3);
                                deliverable_dialog.hide();
                                frm.reload_doc();
                            }
                        }
                    });
                }
            });
            deliverable_dialog.show();
        }
    });
}