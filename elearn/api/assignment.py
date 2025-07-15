import frappe
from frappe import _

@frappe.whitelist()
def create_assignment(course_id, title, due_date, weightage, q_type): # Added q_type parameter
    # Ensure all required fields are provided
    if not (course_id and title and due_date and weightage and q_type):
        frappe.throw("Course, Title, Due Date, Weightage, and Question Type are required.")

    # Validate weightage
    try:
        weightage = int(weightage)
        if not (1 <= weightage <= 100):
            frappe.throw("Weightage must be between 1 and 100.")
    except ValueError:
        frappe.throw("Weightage must be a valid number.")

    # Validate q_type
    if q_type not in ["Coding", "Theory"]:
        frappe.throw("Question Type must be 'Coding' or 'Theory'.")

    # Check if an assignment with this title already exists for this course
    # This is the new logic to prevent duplicates
    existing_assignment = frappe.db.exists(
        "Assignment",
        {
            "title": title,
            "course": course_id
        }
    )
    if existing_assignment:
        # Instead of generic error, give specific message
        frappe.throw(f"An assignment with the title '{title}' already exists for this course.",
                     title="Duplicate Assignment") # Provide a custom title for the error

    try:
        doc = frappe.new_doc("Assignment")
        doc.course = course_id
        doc.title = title
        doc.due_date = due_date
        doc.weightage = weightage
        doc.q_type = q_type # Set the new field
        doc.insert()
        frappe.db.commit()
        return "Assignment created" # Or return doc.name if you need the name on frontend
    except Exception as e:
        frappe.db.rollback()
        frappe.log_error(frappe.get_traceback(), "Assignment Creation Failed")
        frappe.throw(f"Failed to create assignment: {e}")

    return {"message": _("Assignment '{0}' created successfully.").format(title)}

@frappe.whitelist()
def update_assignment(name, title=None, due_date=None, weightage=None):
    if not name:
        frappe.throw(_("Assignment name is required."))

    updates = {}

    if title:
        updates["title"] = title
    if due_date:
        updates["due_date"] = due_date
    if weightage is not None:
        updates["weightage"] = float(weightage)

    if not updates:
        frappe.throw(_("No fields to update."))

    # Force update using frappe.db.set_value
    for field, value in updates.items():
        frappe.db.set_value("Assignment", name, field, value)

    frappe.db.commit()
    return {"message": _("Assignment '{0}' updated successfully.").format(name)}
def validate_instructor(doc, method):
    current_user = frappe.session.user

    # Get the Course associated with the assignment
    if not doc.course:
        frappe.throw(_("Course must be set for this assignment."))

    course = frappe.get_doc("Course", doc.course)

    # Get the instructor of the course (email)
    course_instructor_user = course.instructor

    if not course_instructor_user:
        frappe.throw(_("The course '{0}' has no instructor assigned.").format(course.title))

    # Ensure current user matches course instructor
    if current_user != course_instructor_user and current_user != "Administrator":
        frappe.throw(_("Only the course instructor can create or modify assignments for this course."))
