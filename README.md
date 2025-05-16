<div align="center" markdown="1">
	<img src=".github/images/project_management.png" width="80" height="80"/>
	<h1>Project Management Application</h1>

 **A full-stack, modular project management system built on the **Frappe Framework****
</div>

![Homepage](https://github.com/user-attachments/assets/082c610d-3a64-47e0-af59-a039e09c3781)
</div>
<div align="center">
    <a href="https://one-korecent.frappe.cloud/app/build">Website</a>
    -
    <a href="https://drive.google.com/file/d/11l84TMWJiwHBId_ejRz6mBqPUEBi8qQo/view?usp=drivesdk">Demo Video</a>
</div>

<br>
<br>

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Built With](https://img.shields.io/badge/Built%20With-Frappe-4B8BBE)
![Status](https://img.shields.io/badge/status-In%20Development-yellow)

This application helps organizations efficiently manage complex projects, track deliverables, and coordinate among internal teams, clients, and external vendors — all within a unified, collaborative interface.

---

## Overview

The Project Management App is designed to streamline project execution through structured planning, real-time collaboration, automated notifications, and comprehensive reporting. It includes client and vendor portals, advanced Gantt chart visualization, task assignment workflows, role-based access controls, and integrations with **Raven** for bot-powered messaging and notifications.

The app is best suited for teams working on milestone-driven projects with deliverables and dependencies across multiple stakeholders.

---

## Features

### Core Capabilities

- **Project & Task Management**
  - Create and configure multi-phase projects with defined timelines
  - Hierarchical task structuring using a tree-like architecture
  - Assign tasks to internal team members or external vendors

- **Deliverable Tracking**
  - Associate multiple tasks with a defined deliverable
  - Workflow to submit, review, accept, or request revisions on deliverables

- **Client & Vendor Collaboration**
  - Invite stakeholders without Desk access
  - Secure portals for monitoring progress, submitting deliverables, and providing feedback

- **Automated Workflows**
  - Notification system powered by **Raven bots**
  - Alerts for task assignment, status changes, missed deadlines, and more

- **Reporting System**
  - Scheduled reports for daily and weekly status
  - Time logs, task summaries, and project health indicators

- **Role-Based Dashboards**
  - Custom dashboards based on user type (Project Manager, Team Member, Client, Vendor)

---

## System Architecture

The system is built using **Frappe Framework**, leveraging its modular DocType system, REST APIs, and extensible front-end through **Frappe UI** and **Vue.js**.

- **Backend**: Python (Frappe Framework)
- **Frontend**: Vue.js with Frappe UI (for client and vendor portals)
- **Database**: MariaDB / PostgreSQL (configurable)
- **Communication**: Raven (Bot + Workspace Integration) $ Mail
- **Scheduler**: Frappe Background Jobs + Cron for reports and notifications (ongoing)

---

## Core Modules (DocTypes)

| DocType                    | Description                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| **Project**               | Stores overall project metadata like name, timeline, client, and documents. |
| **Task**                  | Represents individual units of work, often linked to a deliverable.         |
| **Deliverable**           | Major milestones or output expectations in the project lifecycle.           |
| **Deliverable Task**      | Child DocType under Deliverable listing associated tasks.                   |
| **Team Member**           | Tracks assigned members to a project with their roles.                      |
| **PM Client Invitation**  | Manages client invitations with tracking for acceptance and status.         |
| **PM Client Guest Access**| Enables restricted portal access to clients or vendors.                     |
| **Project Proposal**      | Captures proposals made before project approval and initiation.             |
| **Task Time Log**         | Logs effort/time spent by team members on specific tasks.                   |
---

## User Personas

### Project Manager (PM)
- Full access to create/manage projects and assign tasks
- Configure Raven bots for automated alerts
- Access project-level documents, feedback, and Gantt views
- Approve vendor deliverables and generate progress reports
- Dedicated workspace for internal project communication

### Project Team Member
- Access dashboard with assigned tasks and timelines
- Log time and update status
- Receive deadline and update notifications

### Client (External Portal)
- Access limited to assigned projects
- Track project progress and milestones
- View and approve/reject deliverables
- Submit comments or request changes
- Invite internal team members to monitor the project

### Vendor (External Portal)
- View assigned tasks
- Upload deliverables
- View and respond to feedback
- Modify deliverables until approved

---

## Project Lifecycle

1. **Project Creation**
   - PM defines project name, start/end dates, team members, deliverables, etc.
   
2. **Task Assignment**
   - Tasks are created in a hierarchy and assigned to members or vendors

3. **Deliverable Setup**
   - Deliverables are defined and linked with one or more tasks

4. **Notifications**
   - Assignees receive alerts from Raven when tasks are added or modified

5. **Client Feedback**
   - Clients review deliverables and provide feedback via portal

6. **Progress Tracking**
   - PM tracks progress using Gantt and reports

7. **Reports**
   - generate weekly summaries on time logs and status

---

## Raven Bot Integration

Raven is Integrated through a open channel button.

---


### Notification Triggers using Email

| Trigger | Notification |
|--------|--------------|
| Project Created | Message to all the Members and Client |
| Task Assigned | Message to Assignee |
| Task Status Updated | Alert to PM |
| Deliverable Sent for Approval | Alert to Client |
| Deliverable Submitted | Response to the Assigne |
| Feedback Added | Notification to assigned vendor/team |


---

## Client & Vendor Portals

Built using **Vue.js + Frappe UI**, the portals provide role-specific, secure dashboards.

### Client Portal
- Propose new projects
- Monitor real-time progress
- View deliverables and submit feedback
- Add internal viewers

### Vendor Portal
- View and manage assigned tasks
- Submit deliverables
- Update based on feedback
---

## Demo Screenshots

### New Project Creation
![image](https://github.com/user-attachments/assets/0c96478f-d859-4176-83bc-2a3f2d333bec)

### Task in Progress
![image](https://github.com/user-attachments/assets/30c1f343-d58f-42ba-8b58-d745e623bf6a)

### Client Portal
![Dashboard](https://github.com/user-attachments/assets/0d785f4e-13a9-4673-aa26-3336773f7500)
![My Projects](https://github.com/user-attachments/assets/db0584a2-5419-4f18-afa7-4bcd4e6fc689)
![Project Description](https://github.com/user-attachments/assets/d59bf7c4-dd8a-4e2b-af4f-76a372611bb1)
![Deliverables](https://github.com/user-attachments/assets/82e035bb-36e5-4b0d-a1c9-78877052a488)
![Team Members](https://github.com/user-attachments/assets/e4a51239-9d4d-43c3-af16-4cfe23709447)
![Invite Guest to Dashboard](https://github.com/user-attachments/assets/587cd707-c33d-4a8c-b2c7-42c3249ba374)

### Project Proposal Web Page for New Project
![Project Proposal](https://github.com/user-attachments/assets/90404b80-c411-4da7-a2c1-ef517c670c6a)

### Vendor Portal
![Dashboard](https://github.com/user-attachments/assets/a6f3e259-79ea-4148-910e-f929ef5e4531)
![Tasks](https://github.com/user-attachments/assets/4752755b-6adf-4385-b3b1-c43e78c650e2)
![Deliverables](https://github.com/user-attachments/assets/99c20ecb-3b7f-41bd-833a-98db9869d558)
![Submit Deliveravles](https://github.com/user-attachments/assets/3985316e-51cc-4b05-a6bb-56f735768e89)

### Reports for Project Manager
![Project Overview](https://github.com/user-attachments/assets/ae877f57-0c50-43c9-9c48-5ae49de424b1)
![Task Progress Timeline](https://github.com/user-attachments/assets/c169a26c-93d1-418b-be80-bc242baa5fe3)
![Resource Allocation](https://github.com/user-attachments/assets/11e7e18f-9212-4cbf-b1db-3f56f1315912)
![Member Timelogs](https://github.com/user-attachments/assets/263d149e-f190-4949-a69d-c4c3bf577934)
![Task Status](https://github.com/user-attachments/assets/17a53548-912b-42bc-90d6-5849a14afcfd)
![Deliverable Status](https://github.com/user-attachments/assets/7cbf650a-7ffe-4454-857c-19e574d7a803)
![Member Workload](https://github.com/user-attachments/assets/a092b9db-99f9-482a-8211-37ad9136987a)


---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Contributing

We welcome contributions! Please fork the repository and create a pull request. For major changes, open an issue first to discuss what you would like to change.

---

## Contact

For questions, issues, or feature requests, please open a GitHub issue.

<br>
<div align="center">
	<a href="https://frappe.io" target="_blank">
		<picture>
			<source media="(prefers-color-scheme: dark)" srcset="https://frappe.io/files/Frappe-white.png">
			<img src="https://frappe.io/files/Frappe-black.png" alt="Frappe Technologies" height="28"/>
		</picture>
	</a>
</div>
