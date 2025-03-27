// Copyright (c) 2025, Aman and Yashvi and contributors
// For license information, please see license.txt

frappe.ui.form.on('Project', {
    refresh: function(frm) {
        // Add Task Management buttons
        setup_task_management_buttons(frm);
        
        // Add Deliverable button
        setup_deliverable_management_buttons(frm);
    }
});

// Setup Task Management related buttons
function setup_task_management_buttons(frm) {
    // Add Task option under Task Management dropdown
    frm.add_custom_button(__('Add Task'), function() {
        show_add_task_dialog(frm);
    }, __('Task Management'));
    
    // Assign Task option under Task Management dropdown
    frm.add_custom_button(__('Assign Task to Team Member'), function() {
        show_assign_task_dialog(frm);
    }, __('Task Management'));
}

// Show dialog for adding a new task
function show_add_task_dialog(frm) {
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
                default: frappe.datetime.nowdate()
            },
            {
                label: __('End Date'),
                fieldname: 'end_date',
                fieldtype: 'Date'
            },
            {
                label: __('Priority'),
                fieldname: 'priority',
                fieldtype: 'Select',
                options: 'Low\nMedium\nHigh\nCritical',
                default: 'Medium'
            },
            {
                label: __('Status'),
                fieldname: 'status',
                fieldtype: 'Select',
                options: 'Planned\nIn Progress\nOn Hold\nCompleted\nCancelled',
                default: 'Planned'
            },
            {
                label: __('Time (in Hours)'),
                fieldname: 'time_in_hours',
                fieldtype: 'Float',
                default: 0
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
            
            // Create new task
            frappe.call({
                method: 'frappe.client.insert',
                args: {
                    doc: {
                        doctype: 'Task',
                        task_name: values.task_name,
                        project: frm.doc.name,
                        start_date: values.start_date,
                        end_date: values.end_date,
                        priority: values.priority,
                        status: values.status,
                        time_in_hours: values.time_in_hours,
                        description: values.description
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
}

// Show dialog for assigning task to team member
function show_assign_task_dialog(frm) {
    // First, fetch existing tasks for this project
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Task',
            filters: {
                'project': frm.doc.name
            },
            fields: ['name', 'task_name']
        },
        callback: function(r) {
            if(r.message && r.message.length > 0) {
                // Create task option list
                let tasks = r.message.map(task => ({
                    value: task.name,
                    label: task.task_name
                }));
                
                // Get team members for this project
                get_project_team_members(frm, function(team_members) {
                    if (team_members.length > 0) {
                        // Create assignment dialog
                        create_assignment_dialog(tasks, team_members);
                    } else {
                        frappe.msgprint(__("No team members found for this project. Please add team members first."));
                    }
                });
            } else {
                frappe.msgprint(__("No tasks found for this project. Please create a task first."));
            }
        }
    });
}

// Get team members for the project
function get_project_team_members(frm, callback) {
    let team_members = [];
    
    // If team members are already in the project doc
    if (frm.doc.team_member && frm.doc.team_member.length > 0) {
        // Fetch user details for each team member
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'User',
                filters: {
                    // Get users who are part of the project team
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

// Create dialog for task assignment
function create_assignment_dialog(tasks, team_members) {
    let assignment_dialog = new frappe.ui.Dialog({
        title: __('Assign Task to Team Member'),
        fields: [
            {
                label: __('Task'),
                fieldname: 'task',
                fieldtype: 'Select',
                options: tasks,
                reqd: 1
            },
            {
                label: __('Team Member'),
                fieldname: 'team_member',
                fieldtype: 'Select',
                options: team_members,
                reqd: 1
            }
        ],
        primary_action_label: __('Assign'),
        primary_action: function() {
            let values = assignment_dialog.get_values();
            
            // Update the task with assigned user
            frappe.call({
                method: 'frappe.client.set_value',
                args: {
                    doctype: 'Task',
                    name: values.task,
                    fieldname: 'assigned_to',
                    value: values.team_member
                },
                callback: function(r) {
                    if(!r.exc) {
                        frappe.show_alert({
                            message: __("Task assigned successfully"),
                            indicator: 'green'
                        }, 3);
                        assignment_dialog.hide();
                    }
                }
            });
        }
    });
    assignment_dialog.show();
}

// Setup Deliverable Management buttons
function setup_deliverable_management_buttons(frm) {
    // Create Deliverable Management dropdown
    frm.add_custom_button(__('Add Deliverable'), function() {
        show_add_deliverable_dialog(frm);
    }, __('Deliverable Management'));
    
    // Button to link tasks to deliverables
    frm.add_custom_button(__('Link Tasks to Deliverable'), function() {
        show_link_tasks_to_deliverable_dialog(frm);
    }, __('Deliverable Management'));
}

// Show dialog for adding a new deliverable
function show_add_deliverable_dialog(frm) {
    let deliverable_dialog = new frappe.ui.Dialog({
        title: __('Add Deliverable to Project'),
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
                fieldtype: 'Date'
            },
            {
                label: __('Priority'),
                fieldname: 'priority',
                fieldtype: 'Select',
                options: 'Low\nMedium\nCritical',
                default: 'Medium'
            },
            {
                label: __('Status'),
                fieldname: 'status',
                fieldtype: 'Select',
                options: 'Draft\nAwaiting Client Review\nRequired Changes\nApproved',
                default: 'Draft'
            },
            {
                label: __('Description'),
                fieldname: 'description',
                fieldtype: 'Small Text'
            }
        ],
        primary_action_label: __('Create Deliverable'),
        primary_action: function() {
            let values = deliverable_dialog.get_values();
            
            // Create new deliverable
            frappe.call({
                method: 'frappe.client.insert',
                args: {
                    doc: {
                        doctype: 'Deliverable',
                        deliverable_name: values.deliverable_name,
                        project: frm.doc.name,
                        due_date: values.due_date,
                        priority: values.priority,
                        status: values.status,
                        description_for_this_deliverable: values.description
                    }
                },
                callback: function(r) {
                    if(!r.exc) {
                        frappe.show_alert({
                            message: __("Deliverable created successfully"),
                            indicator: 'green'
                        }, 3);
                        deliverable_dialog.hide();
                    }
                }
            });
        }
    });
    deliverable_dialog.show();
}

// Show dialog for linking tasks to deliverables
function show_link_tasks_to_deliverable_dialog(frm) {
    // Fetch deliverables for this project
    frappe.call({
        method: 'frappe.client.get_list',
        args: {
            doctype: 'Deliverable',
            filters: {
                'project': frm.doc.name
            },
            fields: ['name', 'deliverable_name']
        },
        callback: function(r) {
            if(r.message && r.message.length > 0) {
                let deliverables = r.message.map(del => ({
                    value: del.name,
                    label: del.deliverable_name
                }));
                
                // Fetch assigned tasks for this project
                frappe.call({
                    method: 'frappe.client.get_list',
                    args: {
                        doctype: 'Task',
                        filters: {
                            'project': frm.doc.name,
                            'assigned_to': ['!=', '']
                        },
                        fields: ['name', 'task_name', 'assigned_to']
                    },
                    callback: function(task_response) {
                        if(task_response.message && task_response.message.length > 0) {
                            let assigned_tasks = task_response.message.map(task => ({
                                value: task.name,
                                label: `${task.task_name} (Assigned to: ${task.assigned_to})`
                            }));
                            
                            // Create dialog for linking tasks to deliverable
                            let link_tasks_dialog = new frappe.ui.Dialog({
                                title: __('Link Task to Deliverable'),
                                fields: [
                                    {
                                        label: __('Deliverable'),
                                        fieldname: 'deliverable',
                                        fieldtype: 'Select',
                                        options: deliverables,
                                        reqd: 1
                                    },
                                    {
                                        label: __('Task'),
                                        fieldname: 'task',
                                        fieldtype: 'Select',
                                        options: assigned_tasks,
                                        reqd: 1
                                    }
                                ],
                                primary_action_label: __('Link Task'),
                                primary_action: function() {
                                    let values = link_tasks_dialog.get_values();
                                    
                                    // Prepare task entry for the deliverable
                                    frappe.call({
                                        method: 'frappe.client.insert',
                                        args: {
                                            doc: {
                                                doctype: 'Deliverable Task',
                                                parent: values.deliverable,
                                                parenttype: 'Deliverable',
                                                parentfield: 'tasks',
                                                task: values.task
                                            }
                                        },
                                        callback: function(r) {
                                            if(!r.exc) {
                                                frappe.show_alert({
                                                    message: __("Task linked to deliverable successfully"),
                                                    indicator: 'green'
                                                }, 3);
                                                link_tasks_dialog.hide();
                                            } else {
                                                frappe.msgprint(__("Error linking task to deliverable"));
                                            }
                                        }
                                    });
                                }
                            });
                            link_tasks_dialog.show();
                        } else {
                            frappe.msgprint(__("No assigned tasks found for this project. Please assign tasks first."));
                        }
                    }
                });
            } else {
                frappe.msgprint(__("No deliverables found for this project. Please create a deliverable first."));
            }
        }
    });
}