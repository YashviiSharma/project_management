<div style="font-family: Georgia, 'Times New Roman', serif; max-width: 650px; margin: 0 auto; padding: 30px; border: 2px solid #2c3e50; border-radius: 0px; background-color: #f8f9fa;">
  <div style="text-align: center; margin-bottom: 30px; border-bottom: 1px solid #2c3e50; padding-bottom: 20px;">
    <h2 style="color: #2c3e50; font-weight: normal; letter-spacing: 1px; text-transform: uppercase;">Official Project Approval Notification</h2>
  </div>

  <p style="font-size: 16px; color: #2c3e50; line-height: 1.8; text-align: justify;">
    Dear <strong>{{ frappe.db.get_value('User', doc.client, 'full_name') }}</strong>,
  </p>

  <p style="font-size: 16px; color: #2c3e50; line-height: 1.8; text-align: justify;">
    It is with great pleasure that we hereby confirm the formal approval of your proposed project, <strong>{{ doc.project_name }}</strong>, by our Project Management Committee. The project has been officially registered in our system with a provisional commencement date of 
    {% if doc.start_date %}<strong>{{ frappe.format_date(doc.start_date) }}</strong>{% else %}<em>to be determined in due course</em>{% endif %}.
  </p>

  <p style="font-size: 16px; color: #2c3e50; line-height: 1.8; text-align: justify;">
    Please find herewith a comprehensive summary of your project particulars:
  </p>

  <div style="margin: 25px 0; padding: 25px; background-color: #f0f2f5; border: 1px solid #2c3e50;">
    <h3 style="color: #2c3e50; margin-top: 0; font-weight: normal; letter-spacing: 1px; border-bottom: 1px solid #2c3e50; padding-bottom: 10px;">Project Specifications:</h3>
    <ul style="padding-left: 20px; color: #2c3e50; font-size: 15px; line-height: 1.8;">
      <li><strong>Project Designation:</strong> {{ doc.project_name }}</li>
      <li><strong>Project Classification:</strong> {{ doc.project_type or 'Not Applicable' }}</li>
      <li><strong>Present Status:</strong> {{ doc.status }}</li>
      <li><strong>Scheduled Commencement Date:</strong> {% if doc.start_date %}{{ frappe.format_date(doc.start_date) }}{% else %}To Be Determined{% endif %}</li>
      <li><strong>Anticipated Completion Date:</strong> {% if doc.end_date %}{{ frappe.format_date(doc.end_date) }}{% else %}To Be Determined{% endif %}</li>
      <li><strong>Assigned Priority Level:</strong> {{ doc.priority }}</li>
    </ul>

    {% if doc.description %}
    <div style="margin-top: 20px;">
      <h4 style="margin-bottom: 10px; color: #2c3e50; font-weight: normal; letter-spacing: 1px;">Project Description and Scope:</h4>
      <p style="font-size: 15px; color: #2c3e50; line-height: 1.8; text-align: justify;">{{ doc.description }}</p>
    </div>
    {% endif %}
  </div>

  {% if doc.team_member %}
  <div style="margin-top: 30px;">
    <h3 style="color: #2c3e50; font-weight: normal; letter-spacing: 1px; border-bottom: 1px solid #2c3e50; padding-bottom: 10px;">Designated Project Personnel:</h3>
    <table style="width: 100%; border-collapse: collapse; font-size: 15px; margin-top: 15px;">
      <thead>
        <tr style="background-color: #e8f0fe;">
          <th style="text-align: left; padding: 12px; border: 1px solid #2c3e50; background-color: #2c3e50; color: white;">Personnel Name</th>
          <th style="text-align: left; padding: 12px; border: 1px solid #2c3e50; background-color: #2c3e50; color: white;">Electronic Mail Address</th>
          <th style="text-align: left; padding: 12px; border: 1px solid #2c3e50; background-color: #2c3e50; color: white;">Designation</th>
        </tr>
      </thead>
      <tbody>
        {% for member in doc.team_member %}
        <tr>
          <td style="padding: 12px; border: 1px solid #2c3e50;">{{ member.full_name }}</td>
          <td style="padding: 12px; border: 1px solid #2c3e50;">{{ member.email }}</td>
          <td style="padding: 12px; border: 1px solid #2c3e50;">
            {% if member.is_vendor %}
              External Contractor
            {% else %}
              Internal Representative
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% endif %}

  <div style="text-align: center; margin: 40px 0;">
    <a href="{{ frappe.utils.get_url() }}/frontend/client/projects/{{ doc.name }}"
      style="background-color: #2c3e50; color: white; padding: 14px 35px; text-decoration: none; font-weight: normal; letter-spacing: 1px; display: inline-block; border: 1px solid #2c3e50;">
      Access Project Dashboard
    </a>
  </div>

  <p style="font-size: 15px; color: #2c3e50; line-height: 1.8; text-align: justify;">
    Should you require any clarification or additional information regarding this matter, please do not hesitate to contact our office. We look forward to a productive collaboration and the successful execution of this project.
  </p>

  <div style="margin-top: 40px;">
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.5; margin-bottom: 5px;">
      Yours faithfully,
    </p>
    <p style="font-size: 15px; color: #2c3e50; line-height: 1.5; margin-top: 0;">
      <strong>Project Management Office</strong><br>
      {{ frappe.get_system_settings("project_management") or "Project Manageger" }}
    </p>
  </div>

  <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #2c3e50; text-align: center; color: #5a6268; font-size: 12px; font-style: italic;">
    <p>This correspondence is an official notification generated by the <strong>{{ frappe.get_system_settings("app_name") or "Project Management" }}</strong> system.</p>
  </div>
</div>
