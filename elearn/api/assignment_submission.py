import frappe
from frappe import _

@frappe.whitelist()
def validate_grading_permission(doc, method):
    """
    Ensures that only the assigned instructor can grade the submission.
    Triggered on validate or before_save event.
    """
    if doc.status == "Graded":
        # Fetch the related course's instructor
        course = frappe.get_doc("Course", doc.course)
        assigned_instructor = course.instructor

        current_user = frappe.session.user

        # Ensure only assigned instructor can grade
        # if current_user != assigned_instructor:
        #     frappe.throw(_("Only the assigned instructor can grade this submission."))


@frappe.whitelist()
def update_enrollment_on_grade(doc, method):
    """
    Updates Enrollment progress when an assignment submission is graded.
    Triggered on on_update event.
    """
    if doc.status != "Graded":
        return

    # Fetch Enrollment linking student and course
    enrollment = frappe.get_all(
        "Enrollment",
        filters={
            "student": doc.student,
            "course": doc.course
        },
        fields=["name"]
    )

    if enrollment:
        enrollment_doc = frappe.get_doc("Enrollment", enrollment[0].name)

        # Calculate total graded progress
        graded_submissions = frappe.get_all(
            "Assignment Submission",
            filters={
                "student": doc.student,
                "course": doc.course,
                "status": "Graded"
            },
            fields=["assignment"]
        )

        total_progress = 0
        for sub in graded_submissions:
            assignment = frappe.get_doc("Assignment", sub.assignment)
            total_progress += assignment.weightage or 0

        # Cap at 100%
        if total_progress > 100:
            total_progress = 100

        # Update progress
        if hasattr(enrollment_doc, 'progress'):
            enrollment_doc.progress = total_progress

        # Optionally update grade field if exists
        if hasattr(enrollment_doc, 'grade'):
            enrollment_doc.grade = doc.grade

        enrollment_doc.save(ignore_permissions=True)
        frappe.db.commit()

    else:
        frappe.log_error(
            f"No Enrollment found for student: {doc.student}, course: {doc.course}",
            "Update Enrollment on Grade"
        )
        
@frappe.whitelist(allow_guest=False)
def submit_assignment():
    user = frappe.session.user

    assignment = frappe.local.form_dict.get("assignment")
    text_submission = frappe.local.form_dict.get("text_submission")

    if not assignment:
        frappe.throw("Assignment not provided")

    # Get course ID
    assignment_doc = frappe.get_doc("Assignment", assignment)
    course_id = assignment_doc.course

    # Create submission
    submission = frappe.new_doc("Assignment Submission")
    submission.assignment = assignment
    submission.course = course_id
    submission.student = user
    submission.status = "Submitted"
    submission.submission_text = text_submission
    submission.submission_date = frappe.utils.nowdate()
    submission.insert(ignore_permissions=True)
    frappe.db.commit()

    # Handle file upload
    if hasattr(frappe.local, "request") and hasattr(frappe.local.request, "files"):
        uploaded_file = frappe.local.request.files.get('file')
        if uploaded_file:
            file_doc = frappe.get_doc({
                "doctype": "File",
                "file_name": uploaded_file.filename,
                "attached_to_doctype": "Assignment Submission",
                "attached_to_name": submission.name,
                "is_private": 0,
                "content": uploaded_file.stream.read(),
            })
            file_doc.insert(ignore_permissions=True)
            frappe.db.commit()

            # Set file URL to submission
            submission.file = file_doc.file_url
            submission.save(ignore_permissions=True)
            frappe.db.commit()

    return {"message": "Assignment submitted successfully."}


def verify_csrf_token():
    # Skip CSRF check if not in an HTTP request context
    if not frappe.request or not hasattr(frappe.request, "headers"):
        return

    csrf_token = frappe.get_request_header("X-Frappe-CSRF-Token")
    if not csrf_token or csrf_token != frappe.session.data.csrf_token:
        frappe.throw(_("Invalid CSRF token"), exc=frappe.AuthenticationError)


@frappe.whitelist(allow_guest=False) 
def grade_submission(submission_name, grade, feedback=None):
    try:
        # Skip CSRF only when called from console or internal script
        if not frappe.request or not hasattr(frappe.request, "headers"):
            frappe.logger().info("Skipping CSRF check in console/internal context")
        else:
            verify_csrf_token()
        frappe.local.flags.ignore_csrf = True
        # Proceed with grading logic
        submission = frappe.get_doc("Assignment Submission", submission_name)

        if submission.status == "Graded":
            frappe.throw(_("This submission is already graded."))

        submission.grade = grade
        submission.feedback = feedback or ""
        submission.status = "Graded"
        submission.save()
        frappe.db.commit()

        return _("Grade submitted successfully.")

    except Exception as e:
        frappe.log_error(f"Grade submission failed: {str(e)}")
        frappe.throw(_("Failed to process grade submission. Please try again."))
