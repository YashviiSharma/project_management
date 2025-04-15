# Copyright (c) 2025, Aman and Yashvi and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_url, now, add_days


class PMClientInvitation(Document):
    def before_insert(self):
        frappe.utils.validate_email_address(self.email, True)
        if not self.projects:
            frappe.throw("Projects are required to invite a user")

        self.key = frappe.generate_hash(length=12)
        self.invited_by = frappe.session.user
        self.status = "Pending"

    def after_insert(self):
        self.invite_via_email()

    def invite_via_email(self):
        invite_link = get_url(
            f"/api/method/project_management.api.accept_invitation?key={self.key}"
        )
        if frappe.local.dev_server:
            print(f"Invite link for {self.email}: {invite_link}")

        inviter_user = frappe.get_doc("User", self.invited_by)
        inviter_name = inviter_user.full_name or inviter_user.first_name

        # Fetch project details with project_name
        project_list = []
        if self.projects:
            project_names = frappe.parse_json(self.projects)
            for project_name in project_names:
                project = frappe.get_doc("Project", project_name)
                project_list.append({
                    "name": project_name,
                    "project_name": project.project_name
                })

        title = "Project Management Portal"
        template = frappe.render_template(
            "templates/includes/pm_client_invitation.html", 
            {
                'doc': self.as_dict(),
                'title': title,
                'invite_link': invite_link,
                'inviter_name': inviter_name,
                'invited_by': self.invited_by,
                'projects': project_list
            }
        )

        try:
            frappe.sendmail(
                recipients=[self.email],
                subject=f"You have been invited to join {title}",
                args={"title": title, "invite_link": invite_link},
                message=template,
                now=True,
            )
            self.db_set("email_sent_at", now())
        except Exception as e:
            frappe.log_error(
                f"Failed to send invitation email: {str(e)}", "Client Invitation"
            )

    @frappe.whitelist()
    def accept_invitation(self):
        frappe.only_for("System Manager")
        self.accept()

    def accept(self):
        if self.status == "Expired":
            frappe.throw("Invalid or expired key")

        user = self.create_user_if_not_exists()
        user.append_roles(self.role)
        user.save(ignore_permissions=True)

        self.create_guest_access(user)

        self.status = "Accepted"
        self.accepted_at = now()
        self.save(ignore_permissions=True)

    def get_password_link(self):
        return password_link(frappe.get_doc("User", self.email))

    def create_guest_access(self, user):
        """Create guest access for the invited user"""
        projects = frappe.parse_json(self.projects) if self.projects else []

        # Find all the projects belonging to the client who sent the invitation
        client_user = self.invited_by

        # Create guest access record connecting the guest to the client
        guest_access = frappe.get_doc(
            {
                "doctype": "PM Client Guest Access",
                "user": user.name,
                "client": client_user,
                "creation_date": now(),
            }
        )
        guest_access.save(ignore_permissions=True)

    def create_user_if_not_exists(self):
        """Create a new user if they don't exist already"""
        if not frappe.db.exists("User", self.email):
            first_name = self.email.split("@")[0].title()
            user = frappe.get_doc(
                doctype="User",
                user_type="Website User",
                email=self.email,
                send_welcome_email=0,
                first_name=first_name,
            ).insert(ignore_permissions=True)
        else:
            user = frappe.get_doc("User", self.email)

        return user


def expire_invitations():
    """Expire invitations after 3 days - can be called via scheduler"""
    days = 3
    invitations_to_expire = frappe.db.get_all(
        "PM Client Invitation",
        filters={"status": "Pending", "creation": ["<", add_days(now(), -days)]},
    )

    for invitation in invitations_to_expire:
        invitation = frappe.get_doc("PM Client Invitation", invitation.name)
        invitation.status = "Expired"
        invitation.save(ignore_permissions=True)


def password_link(user, password_expired=False):
    """Generate a password reset link for new users"""
    from frappe.utils import now_datetime, sha256_hash

    key = frappe.generate_hash()
    hashed_key = sha256_hash(key)
    user.reset_password_key = hashed_key
    user.last_reset_password_key_generated_on = now_datetime()
    user.save(ignore_permissions=True)
    frappe.db.commit()

    url = "/update-password?key=" + key
    if password_expired:
        url = "/update-password?key=" + key + "&password_expired=true"

    return url
