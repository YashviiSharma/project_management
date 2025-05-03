<div style="font-family: Georgia, 'Times New Roman', serif; max-width: 650px; margin: 0 auto; padding: 30px; border: 2px solid #2c3e50; border-radius: 0px; background-color: #f8f9fa;">
  <div style="text-align: center; margin-bottom: 30px; border-bottom: 1px solid #2c3e50; padding-bottom: 20px;">
    <h2 style="color: #2c3e50; font-weight: normal; letter-spacing: 1px; text-transform: uppercase;">New Task Assignment Notification</h2>
  </div>

  <p style="font-size: 16px; color: #2c3e50; line-height: 1.8; text-align: justify;">
    Dear <strong>{{ frappe.db.get_value('User', doc.assigned_to, 'full_name') }}</strong>,
  </p>

  <p style="font-size: 16px; color: #2c3e50; line-height: 1.8; text-align: justify;">
    You have been assigned a new task in the project <strong>{{ doc.project }}</strong>. Please review the task details below and take appropriate action as required.
  </p>

  <div style="margin: 25px 0; padding: 25px; background-color: #f0f2f5; border: 1px solid #2c3e50;">
    <h3 style="color: #2c3e50; margin-top: 0; font-weight: normal; letter-spacing: 1px; border-bottom: 1px solid #2c3e50; padding-bottom: 10px;">Task Details:</h3>
    <ul style="padding-left: 20px; color: #2c3e50; font-size: 15px; line-height: 1.8;">
      <li><strong>Task Name:</strong> {{ doc.task_name }}</li>
      <li><strong>Project:</strong> {{ doc.project }}</li>
      <li><strong>Status:</strong> {{ doc.status }}</li>
      <li><strong>Priority:</strong> {{ doc.priority }}</li>
      <li><strong>Start Date:</strong> {% if doc.start_date %}{{ frappe.format_date(doc.start_date) }}{% else %}Not Specified{% endif %}</li>
      <li><strong>End Date:</strong> {% if doc.end_date %}{{ frappe.format_date(doc.end_date) }}{% else %}Not Specified{% endif %}</li>
      {% if doc.parent_task %}<li><strong>Parent Task:</strong> {{ doc.parent_task }}</li>{% endif %}
    </ul>

    {% if doc.description %}
    <div style="margin-top: 20px;">
      <h4 style="margin-bottom: 10px; color: #2c3e50; font-weight: normal; letter-spacing: 1px;">Task Description:</h4>
      <p style="font-size: 15px; color: #2c3e50; line-height: 1.8; text-align: justify;">{{ doc.description }}</p>
    </div>
    {% endif %}
  </div>

  <div style="text-align: center; margin: 40px 0;">
    <a href="{{ frappe.utils.get_url() }}/app/task/{{ doc.name }}"
      style="background-color: #2c3e50; color: white; padding: 14px 35px; text-decoration: none; font-weight: normal; letter-spacing: 1px; display: inline-block; border: 1px solid #2c3e50;">
      View Task Details
    </a>
  </div>

  <p style="font-size: 15px; color: #2c3e50; line-height: 1.8; text-align: justify;">
    Please begin work on this task at your earliest convenience. If you have any questions or require clarification about this task, please contact the project manager.
  </p>

  <div style="margin-top: 40px;">
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.5; margin-bottom: 5px;">
      Regards,
    </p>
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.5; margin-top: 0;">
      <strong>Project Management Office</strong><br>
      {{ frappe.get_system_settings("project_management") or "Project Manager" }}
    </p>
  </div>

  <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #2c3e50; text-align: center; color: #5a6268; font-size: 12px; font-style: italic;">
    <p>This is an automated notification from the <strong>{{ frappe.get_system_settings("app_name") or "Project Management" }}</strong> system. Please do not reply to this email.</p>
  </div>
</div>
