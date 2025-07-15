import frappe

def update_progress_on_grading(doc, method):
    """
    Hook this function to Assignment Submission's on_update or after_save event.
    Updates Enrollment progress when submission is graded.
    """
    if doc.status != "Graded":
        return  # Only update when graded

    # Fetch all graded submissions for this student & course
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

    # Fetch Enrollment for this student and course
    enrollment = frappe.get_all(
        "Enrollment",
        filters={
            "student": doc.student,
            "course": doc.course
        },
        fields=["name", "progress"]
    )

    if enrollment:
        enrollment_doc = frappe.get_doc("Enrollment", enrollment[0].name)
        enrollment_doc.progress = total_progress
        enrollment_doc.save()
        frappe.db.commit()
