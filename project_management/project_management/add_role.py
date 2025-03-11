import frappe

def create_roles():
    roles = {
        "Vendor": {"desk_access": 0},
        "Client": {"desk_access": 0},
        "Team Member": {"desk_access": 1, "home_page": "/app"},
        "Project Manager": {"desk_access": 1, "home_page": "/app"}
    }

    for role, properties in roles.items(): 
        # Check if the role already exists
        if not frappe.db.exists("Role", {"role_name": role}):
            doc = frappe.get_doc({
                "doctype": "Role",
                "role_name": role,
                "desk_access": properties.get("desk_access", 0),
                "home_page": properties.get("home_page", ""),
                "enabled": 1
            })
            doc.insert(ignore_permissions=True)
            print(f"✅ Role '{role}' created successfully.")
            # Assign roles to Administrator user
            assign_roles_to_admin(roles.keys())


def assign_roles_to_admin(roles):
    admin_user = "Administrator"

    if not frappe.db.exists("User", {"name": admin_user}):
        print("❌ Administrator user not found. Skipping role assignment.")
        return

    user_doc = frappe.get_doc("User", admin_user)

    assigned_roles = {role.role for role in user_doc.roles}

    for role in roles:
        if role not in assigned_roles:
            user_doc.append("roles", {"role": role})

    user_doc.save(ignore_permissions=True)
    print("✅ All required roles assigned to Administrator.")
