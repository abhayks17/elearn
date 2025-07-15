import frappe
from frappe.utils import getdate, today


def get_context(context):
    course_name = frappe.form_dict.get("name")
    if not course_name:
        frappe.throw("Course name not provided in URL")

    frappe.clear_document_cache("Course", course_name)
    course = frappe.get_doc("Course", course_name)

    current_user = frappe.session.user
    is_instructor = False
    if course.instructor:
        instructor_doc = frappe.get_doc("User", course.instructor)
        is_instructor = (current_user != "Guest" and current_user == instructor_doc.name)

    is_enrolled = False
    submissions = {}  # Student's own submissions
    all_submissions_by_assignment = {}  # For instructor

    if current_user != "Guest":
        enrollments = frappe.get_all(
            "Enrollment",
            filters={"student": current_user, "course": course.name},
            fields=["name"]
        )
        is_enrolled = bool(enrollments)

        if is_enrolled:
            submission_docs_current_user = frappe.get_all(
                "Assignment Submission",
                filters={"student": current_user, "course": course.name},
                fields=["assignment", "status", "grade", "feedback", "name", "submission_text", "file"]
            )
            for sub in submission_docs_current_user:
                if sub.file:
                    file_url = frappe.db.get_value("File", sub.file, "file_url")
                    sub["file_url"] = file_url
                submissions[sub.assignment] = sub

    # Fetch assignments
    assignments = frappe.get_all(
        "Assignment",
        filters={"course": course.name},
        fields=["name", "title", "due_date", "weightage"]
    )

    # Instructor view: fetch all submissions
    if is_instructor:
        for assignment in assignments:
            assignment_submissions = frappe.get_all(
                "Assignment Submission",
                filters={"assignment": assignment.name},
                fields=["name", "student", "status", "grade", "feedback", "submission_text", "file"],
                order_by="creation desc"
            )
            for sub in assignment_submissions:
                if sub.file:
                    file_url = frappe.db.get_value("File", sub.file, "file_url")
                    sub["file_url"] = file_url
            all_submissions_by_assignment[assignment.name] = assignment_submissions

    # Lessons (trial or full)
    lessons = course.lessons
    if not is_enrolled and not is_instructor:
        lessons = [l for l in lessons if l.is_trial]

    # 🔁 Process each lesson: check expiry and video type
    today_date = getdate(today())
    for lesson in lessons:
        lesson.show_video = True
        lesson.embed_url = None
        lesson.local_video = None

        # Check for expiry
        if lesson.video_expiry_date and getdate(lesson.video_expiry_date) < today_date:
            lesson.show_video = False
            continue

        # YouTube embed support
        video_url = lesson.video_url
        if video_url:
            if "youtube.com/watch?v=" in video_url:
                video_id = video_url.split("v=")[-1].split("&")[0]
                lesson.embed_url = f"https://www.youtube.com/embed/{video_id}"
            elif "youtu.be/" in video_url:
                video_id = video_url.split("youtu.be/")[-1].split("?")[0]
                lesson.embed_url = f"https://www.youtube.com/embed/{video_id}"

        # If no YouTube link, use uploaded file
        if not lesson.embed_url and lesson.video_file:
            lesson.local_video = lesson.video_file

    # Populate context
    context.course = course
    context.lessons = lessons
    context.is_instructor = is_instructor
    context.is_enrolled = is_enrolled
    context.assignments = assignments
    context.submissions = submissions
    context.all_submissions_by_assignment = all_submissions_by_assignment
    context.current_user = current_user
    context.no_cache = 1

    return context
