import frappe


def create_user_for_instructor(doc, method):
    """
    Hook to create User automatically when Instructor Application is approved
    """
    if doc.workflow_state == "Approved":
        # Check if user already exists
        existing_users = frappe.get_all("User", filters={"email": doc.email})
        if existing_users:
            frappe.msgprint(f"User with email {doc.email} already exists.")
            return

        # Create new user
        user = frappe.new_doc("User")
        user.email = doc.email
        user.first_name = doc.full_name or "Instructor"
        user.enabled = 1
        user.new_password = "Instructor@1234"
        user.send_welcome_email = 1
        user.append("roles", {
            "role": "Instructor"  # Ensure 'Instructor' role exists
        })
        user.save(ignore_permissions=True)
        frappe.db.commit()

        frappe.msgprint(f"User created for Instructor: {doc.email}")
