import frappe
from urllib.parse import quote

def get_context(context):
    form = frappe.local.form_dict
    difficulty = form.get("difficulty")
    rating = form.get("rating")
    certificate = form.get("certificate")

    filters = {
        "status": "Published"
    }
    if difficulty:
        filters["difficulty"] = difficulty
    if rating:
        try:
            filters["rating"] = [">=", float(rating)]
        except ValueError:
            pass
    if certificate == "1":
        filters["has_certificate"] = 1

    # Fetch courses
    courses = frappe.db.get_list(
        "Course",
        filters=filters,
        fields=[
            "name", "title", "course_description", "instructor",
            "difficulty", "rating", "has_certificate", "is_trial", "status"
        ],
        order_by="modified desc"
    )

    user = frappe.session.user
    enrolled_courses = frappe.db.get_all(
        "Enrollment",
        filters={"student": user},
        fields=["course"]
    )
    enrolled_set = set(e.course for e in enrolled_courses)

    # Add additional fields
    for course in courses:
        course.trial_available = course.is_trial
        course.already_enrolled = course.name in enrolled_set
        course.encoded_name = quote(course.name) if course.name else ""

    # ✅ Add instructor check
    roles = frappe.get_roles(user)
    context.is_instructor = "Instructor" in roles

    # Final context
    context.courses = courses
    context.selected_difficulty = difficulty
    context.selected_rating = rating
    context.selected_certificate = certificate
    context.no_cache = 1
    return context
