import frappe
from frappe.utils import nowdate, add_days

def send_assignment_reminders():
    upcoming_date = add_days(nowdate(), 1)

    assignments = frappe.get_all("Assignment",
        filters={"due_date": upcoming_date},
        fields=["name", "title", "course", "due_date"]
    )

    for assignment in assignments:
        course = frappe.get_doc("Course", assignment.course)
        enrolled_students = frappe.get_all("Enrollment",
            filters={"course": assignment.course},
            fields=["student"]
        )

        for enrollment in enrolled_students:
            student_email = enrollment.student  # ✅ already email like "athul@gmail.com"

            if student_email:
                subject = f"📅 Reminder: '{assignment.title}' due tomorrow"
                message = f"""
                    Dear Student,<br><br>
                    This is a reminder that the assignment <b>{assignment.title}</b> for the course <b>{course.title}</b> is due on <b>{assignment.due_date}</b>.<br><br>
                    Please make sure to submit it before the deadline.<br><br>
                    Regards,<br>
                    E-Learning System
                """
                frappe.sendmail(
                    recipients=[student_email],
                    subject=subject,
                    message=message
                )
