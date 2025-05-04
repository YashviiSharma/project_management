<div style="font-family: Georgia, 'Times New Roman', serif; max-width: 650px; margin: 0 auto; padding: 30px; border: 2px solid #2c3e50; border-radius: 0px; background-color: #f8f9fa;">
  <div style="text-align: center; margin-bottom: 30px; border-bottom: 1px solid #2c3e50; padding-bottom: 20px;">
    <h2 style="color: #2c3e50; font-weight: normal; letter-spacing: 1px; text-transform: uppercase;">New Project Proposal Submission</h2>
  </div>

  <p style="font-size: 16px; color: #2c3e50; line-height: 1.8; text-align: justify;">
    Dear <strong>{{ frappe.db.get_value('User', frappe.session.user, 'full_name') }}</strong>,
  </p>

  <p style="font-size: 16px; color: #2c3e50; line-height: 1.8; text-align: justify;">
    We are pleased to acknowledge the receipt of your new project proposal, <strong>{{ doc.project_name }}</strong>. Your proposal has been successfully registered in our system and will be reviewed by our Project Management Committee at the earliest convenience.
  </p>

  <p style="font-size: 16px; color: #2c3e50; line-height: 1.8; text-align: justify;">
    Please find below a summary of your submitted project proposal:
  </p>

  <div style="margin: 25px 0; padding: 25px; background-color: #f0f2f5; border: 1px solid #2c3e50;">
    <h3 style="color: #2c3e50; margin-top: 0; font-weight: normal; letter-spacing: 1px; border-bottom: 1px solid #2c3e50; padding-bottom: 10px;">Proposal Details:</h3>
    <ul style="padding-left: 20px; color: #2c3e50; font-size: 15px; line-height: 1.8;">
      <li><strong>Project Title:</strong> {{ doc.project_name }}</li>
      <li><strong>Project Classification:</strong> {{ doc.project_type or 'Not Specified' }}</li>
      <li><strong>Current Status:</strong> {{ doc.docstatus == 0 and 'Draft' or doc.docstatus == 1 and 'Submitted' or 'Cancelled' }}</li>
      <li><strong>Proposed Start Date:</strong> {% if doc.planed_start_date %}{{ frappe.format_date(doc.planed_start_date) }}{% else %}To Be Determined{% endif %}</li>
      <li><strong>Proposed End Date:</strong> {% if doc.planed_end_date %}{{ frappe.format_date(doc.planed_end_date) }}{% else %}To Be Determined{% endif %}</li>
    </ul>

    {% if doc.description %}
    <div style="margin-top: 20px;">
      <h4 style="margin-bottom: 10px; color: #2c3e50; font-weight: normal; letter-spacing: 1px;">Project Description and Scope:</h4>
      <p style="font-size: 15px; color: #2c3e50; line-height: 1.8; text-align: justify;">{{ doc.description }}</p>
    </div>
    {% endif %}
  </div>

  <div style="margin-top: 30px;">
    <h3 style="color: #2c3e50; font-weight: normal; letter-spacing: 1px; border-bottom: 1px solid #2c3e50; padding-bottom: 10px;">Project Manager Contact:</h3>
    <div style="padding: 15px; background-color: #f0f2f5; border: 1px solid #2c3e50; margin-top: 15px;">
      <p style="font-size: 15px; color: #2c3e50; line-height: 1.8; margin: 0;">
        <strong>Email:</strong> projectmanagementfrappe@gmail.com
      </p>
      <p style="font-size: 15px; color: #2c3e50; line-height: 1.8; margin-top: 10px;">
        Should you have any questions regarding your proposal, please contact the project manager directly via the email address provided above.
      </p>
    </div>
  </div>

  <p style="font-size: 15px; color: #2c3e50; line-height: 1.8; text-align: justify; margin-top: 30px;">
    Our team will review your proposal thoroughly and contact you should additional information be required. You will receive a formal notification regarding the status of your proposal within 5-7 business days.
  </p>

  <div style="margin-top: 40px;">
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.5; margin-bottom: 5px;">
      Best regards,
    </p>
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.5; margin-top: 0;">
      <strong>Project Management Office</strong><br>
      {{ frappe.get_system_settings("project_management") or "Project Management Team" }}
    </p>
  </div>

  <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #2c3e50; text-align: center; color: #5a6268; font-size: 12px; font-style: italic;">
    <p>This is an automated notification from the <strong>{{ frappe.get_system_settings("app_name") or "Project Management System" }}</strong>.</p>
    <p>Reference ID: {{ doc.name }}</p>
  </div>
</div>