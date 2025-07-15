import frappe

def get_context(context):
    submissions = frappe.get_all(
        "Assignment Submission",
        fields=[
            "name",
            "student",
            "course",
            "assignment",
            "submission_date",
            "grade",
            "feedback"
        ],
        order_by="submission_date desc"
    )

    analytics = []

    for sub in submissions:
        assignment_doc = frappe.get_doc("Assignment", sub.assignment)
        questions = []
        if hasattr(assignment_doc, "questions"):
            
            for q in assignment_doc.questions:
                questions.append({
                    "question": q.question,
                    "answer": q.answer,
                    "marks_scored": q.marks or 0,
                    "question_type": assignment_doc.q_type or ""
                })
            
        analytics.append({
            "student": sub.student,
            "course": sub.course,
            "assignment": assignment_doc.title,
            
            "submission_date": sub.submission_date,
            "grade": sub.grade,
            "total_marks": assignment_doc.weightage,
            "feedback": sub.feedback,
            "question_type": assignment_doc.q_type or "",
            "questions": questions,
        })

    context.analytics = analytics
    return context
