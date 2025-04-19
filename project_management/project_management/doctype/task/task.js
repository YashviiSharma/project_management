// Copyright (c) 2025, Aman and Yashvi and contributors
// For license information, please see license.txt

frappe.ui.form.on("Task", {
    refresh: function(frm) {
        if(!frm.is_new()) {
            frm.trigger("make_dashboard");
            
            if (!frm.progress_bar_initialized) {
                frm.trigger("show_progress_bar");
                frm.progress_bar_initialized = true;
            } else {
                frm.trigger("update_progress_bar");
            }
        }

        // Disable start button if task is 100% complete
        if(frm.doc.progress_ === 100) {
            frm.page.set_indicator(__("Completed"), "green");
            frm.disable_save();
        }
    },

    show_progress_bar: function(frm) {
        // Create progress bar container only once
        let progress_html = `
            <div class="custom-progress-container" style="margin-bottom: 15px;">
                <div class="progress" style="height: 20px;">
                    <div class="progress-bar custom-task-progress" role="progressbar" 
                        aria-valuemin="0" 
                        aria-valuemax="100">
                    </div>
                </div>
            </div>
        `;
        
        let section_break = $(frm.fields_dict.section_break_ard0.wrapper);
        if(section_break.length && !section_break.prev().hasClass('custom-progress-container')) {
            section_break.before(progress_html);
        }
        
        frm.trigger("update_progress_bar");
    },

    update_progress_bar: function(frm) {
        let progress = frm.doc.progress_ || 0;
        
        // Determine color based on progress
        let progressColor;
        if (progress < 10) {
            progressColor = '#dc3545'; // red
        } else if (progress >= 10 && progress < 20) {
            progressColor = '#d63384'; // pink
        } else if (progress >= 20 && progress < 50) {
            progressColor = '#fd7e14'; // orange
        } else if (progress >= 50 && progress < 80) {
            progressColor = '#ffc107'; // yellow-orange
        } else if (progress >= 80 && progress < 100) {
            progressColor = '#20c997'; // light green
        } else if (progress >= 100) {
            progressColor = '#198754'; // dark green
        }

        let progress_bar = $(frm.wrapper).find('.custom-task-progress');
        if (progress_bar.length) {
            progress_bar.css({
                'width': progress + '%',
                'background-color': progressColor
            }).text(progress + '%');
            
            progress_bar.attr('aria-valuenow', progress);
        }
    },

    make_dashboard: function(frm) {
        if(frm.doc.__islocal) return;

        let currentIncrement = 0;
        let interval;

        function updateStopwatch(increment) {
            const hours = Math.floor(increment / 3600);
            const minutes = Math.floor((increment % 3600) / 60);
            const seconds = Math.floor(increment % 60);
            
            const hoursElement = $(frm.wrapper).find(".stopwatch .hours");
            const minutesElement = $(frm.wrapper).find(".stopwatch .minutes");
            const secondsElement = $(frm.wrapper).find(".stopwatch .seconds");
            const colonElements = $(frm.wrapper).find(".stopwatch .colon");
            const stopwatchElement = $(frm.wrapper).find(".stopwatch");
            
            hoursElement.text(hours.toString().padStart(2, '0'));
            minutesElement.text(minutes.toString().padStart(2, '0'));
            secondsElement.text(seconds.toString().padStart(2, '0'));
            
            const totalMinutes = (hours * 60) + minutes;
            
            // Set color based on time duration
            let textColor;
            if (increment < 60) { 
                textColor = '#198754';
            } else if (totalMinutes < 5) {
                textColor = '#20c997'; 
            } else if (totalMinutes < 10) { 
                textColor = '#0041c2'; 
            } else if (totalMinutes < 30) { 
                textColor = '#fd7e14'; 
            } else if (totalMinutes < 60) { 
                textColor = '#d63384'; 
            } else { 
                textColor = '#dc3545'; 
            }
            
            // Apply color to all timer elements
            hoursElement.css('color', textColor);
            minutesElement.css('color', textColor);
            secondsElement.css('color', textColor);
            colonElements.css('color', textColor);
            
        }

        // Only add timer if it doesn't exist
        if (!$(frm.wrapper).find('.stopwatch').length) {
            const timer = `
                <div class="stopwatch" style="font-weight:bold;margin:0px 13px 0px 2px;
                    color:#545454;font-size:18px;display:inline-block;vertical-align:text-bottom;">
                    <span class="hours">00</span>
                    <span class="colon">:</span>
                    <span class="minutes">00</span>
                    <span class="colon">:</span>
                    <span class="seconds">00</span>
                </div>`;
            
            frm.toolbar.page.add_inner_message(timer);
        }

        currentIncrement = frm.events.get_current_time(frm);
        updateStopwatch(currentIncrement);

        frm.page.clear_actions_menu();

        if(!frm.doc.actual_start_date && frm.doc.progress_ < 100) {
            frm.add_custom_button(__("Start Task"), () => frm.events.start_timer(frm));
        } else if(frm.doc.status === "In Progress") {
            frm.add_custom_button(__("Pause"), () => frm.events.pause_timer(frm));
            frm.add_custom_button(__("Complete"), () => frm.events.complete_task(frm));
        } else if(frm.doc.status === "Paused") {
            frm.add_custom_button(__("Resume"), () => frm.events.resume_timer(frm));
        }

        // Update timer if task is running
        if(frm.doc.status === "In Progress") {
            currentIncrement = frm.events.get_current_time(frm);
            interval = setInterval(() => {
                currentIncrement++;
                updateStopwatch(currentIncrement);
            }, 1000);
        }

        $(document).on("form-refresh", () => clearInterval(interval));
    },

    start_timer: function(frm) {
        frm.call('start_timer')
            .then(() => frm.refresh());
    },

    pause_timer: function(frm) {
        let current_progress = frm.doc.progress_ || 0;
        
        frappe.prompt({
            fieldtype: "Float",
            label: __("Completed Percentage in this Session"),
            fieldname: "completed_percent",
            reqd: 1,
            default: current_progress,
            description: __("Current total completion: {0}%", [current_progress])
        }, (data) => {
            if (data.completed_percent < 0) {
                frappe.throw(__("Percentage cannot be negative"));
            }
            
            frm.dashboard.set_headline_alert("Updating task progress...");
            
            frm.call('pause_timer', data)
                .then(() => {
                    frm.refresh();
                    frappe.show_alert(__("Task Paused at {0}% progress", [frm.doc.progress_]), 3);
                })
                .catch(() => {
                    frm.dashboard.clear_headline();
                });
        }, __("Update Progress"), __("Pause"));
    },

    resume_timer: function(frm) {
        frm.call('resume_timer')
            .then(() => { frm.refresh();
            frappe.show_alert(__("Task Resumed"), 3);
        });
    },

    complete_task: function(frm) {
        frappe.confirm(
            __("Are you sure you want to mark this task as complete?"),
            function() {
                frm.dashboard.set_headline_alert("Completing task...");
                
                frm.call('complete_task')
                    .then(() => {
                        frm.refresh();
                        frappe.show_alert(__("Task marked as Completed"), 3);
                    })
                    .catch(() => {
                        frm.dashboard.clear_headline();
                    });
            },
            __("Confirm Completion")
        );
    },

    get_current_time: function(frm) {
        let total_seconds = 0;
        (frm.doc.time_logs || []).forEach(log => {
            if(log.from_time && log.to_time) {
                total_seconds += moment(log.to_time).diff(moment(log.from_time), 'seconds');
            } else if(log.from_time) {
                total_seconds += moment().diff(moment(log.from_time), 'seconds');
            }
        });
        return total_seconds;
    }
});
