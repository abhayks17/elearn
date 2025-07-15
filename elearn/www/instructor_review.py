# apps/elearn/elearn/www/instructor_review.py
import frappe
from frappe.utils import get_fullname

def get_context(context):
    # Restrict access to instructors
    if not frappe.session.user or not "Instructor" in frappe.get_roles():
        frappe.throw("You are not authorized to access this page.")

    # Get submissions that are not yet graded
    submissions = frappe.get_all(
        "Assignment Submission",
        filters={"status": ["!=", "Graded"]},
        fields=["name", "student", "assignment", "submission_date", "feedback", "status"]
    )

    submission_data = []
    for sub in submissions:
        assignment_doc = frappe.get_doc("Assignment", sub.assignment)
        student_name = get_fullname(sub.student)

        questions = []
        for q in assignment_doc.questions:
            questions.append({
                "question": q.question,
                "answer": q.answer,
                "marks": q.marks
            })

        submission_data.append({
            "name": sub.name,
            "student_id": sub.student,
            "student_name": student_name,
            "assignment": sub.assignment,
            "assignment_title": assignment_doc.title,
            "submission_date": sub.submission_date.strftime("%Y-%m-%d"),
            "feedback": sub.feedback or "",
            "status": sub.status,
            "questions": questions,
        })

    context.submissions = submission_data
    return context
