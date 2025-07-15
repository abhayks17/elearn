# file: elearn/api/course.py
import frappe
from frappe import _
from frappe.utils import now

@frappe.whitelist()
def enroll():
    data = frappe.local.form_dict
    course_id = data.get("course_id")
    user = frappe.session.user

    if not course_id or not user:
        frappe.throw(_("Missing course or user information."))

    # Create new enrollment with required fields
    enrollment = frappe.new_doc("Enrollment")
    enrollment.course = course_id
    enrollment.student = user  # assuming 'student' is the correct field
    enrollment.enrollment_date = now()  # ✅ Add this line
    enrollment.insert()
    frappe.db.commit()

    return {"message": _("Enrollment successful.")}
import frappe
from frappe import _

@frappe.whitelist()
def update_course(course_name, title=None, description=None):
    current_user = frappe.session.user

    course = frappe.get_doc("Course", course_name)

    if course.instructor != current_user:
        frappe.throw(_("You are not authorized to update this course."))

    if title:
        course.title = title
    if description:
        course.course_description = description

    course.save(ignore_permissions=True)
    frappe.db.commit()

    return {"message": _("Course '{0}' updated successfully.").format(course_name)}
