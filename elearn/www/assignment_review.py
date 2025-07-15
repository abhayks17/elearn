import frappe

def get_context(context):
    user = frappe.session.user

    # Ensure logged in
    if user == "Guest":
        frappe.throw("You must be logged in to view this page.")

    # Check instructor role
    roles = frappe.get_roles(user)
    if "Instructor" not in roles:
        frappe.throw("Only instructors can view this page.")

    # Get courses taught by this instructor
    courses = frappe.get_all("Course", filters={"instructor": user}, fields=["name", "title"])
    if not courses:
        context.error = "You are not assigned to any course."
        context.data = {}
        context.courses = []
        context.assignments = []
        context.csrf_token = frappe.sessions.get_csrf_token()
        context.no_cache = 1
        return context

    course_map = {c.name: c.title for c in courses}
    course_ids = [c.name for c in courses]

    # Get all enrollments
    enrollments = frappe.get_all(
        "Enrollment",
        filters={"course": ["in", course_ids]},
        fields=["name", "student", "course"]
    )
    student_courses = {}
    for e in enrollments:
        student_courses.setdefault(e.course, []).append(e.student)

    # Fetch submissions with file field
    submissions = frappe.get_all(
        "Assignment Submission",
        filters={"course": ["in", course_ids]},
        fields=["name", "assignment", "student", "submission_text", "status", "course", "grade", "feedback", "file"]
    )

    # Get file URLs
    # Get file URLs (direct assignment if file field is a URL)
    for sub in submissions:
        sub["file_url"] = sub["file"] if sub.get("file") else None

    # Fetch assignments
    assignments = frappe.get_all(
        "Assignment",
        filters={"course": ["in", course_ids]},
        fields=["name", "course", "title", "due_date", "weightage", "q_type"]
    )

    assignment_detail_map = {a.name: a for a in assignments}

    data = {}
    for c in course_ids:
        data[c] = {
            "title": course_map[c],
            "students": {},
            "total_assigned_weightage": 0
        }

    for assignment in assignments:
        if assignment.course in data:
            data[assignment.course]["total_assigned_weightage"] += (assignment.weightage or 0)

    for sub in submissions:
        course = sub.course
        student = sub.student

        if student not in data[course]["students"]:
            data[course]["students"][student] = []

        assignment_info = assignment_detail_map.get(sub.assignment, {})

        data[course]["students"][student].append({
            "name": sub.name,
            "assignment": sub.assignment,
            "weightage": assignment_info.get("weightage", 0),
            "q_type": assignment_info.get("q_type"),
            "text": sub.submission_text,
            "status": sub.status,
            "grade": sub.grade,
            "feedback": sub.feedback,
            "file_url": sub.get("file_url")
        })

    context.data = data
    context.courses = courses
    context.assignments = assignments
    context.csrf_token = frappe.sessions.get_csrf_token()
    context.no_cache = 1

    return context
