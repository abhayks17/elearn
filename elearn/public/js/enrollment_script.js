function enrollCourse(courseId) {
    fetch('/api/method/elearn.api.course.enroll', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Frappe-CSRF-Token': frappe.csrf_token
        },
        body: JSON.stringify({ course_id: courseId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            location.reload();  // Or update DOM to hide enroll button
        } else if (data._error_message) {
            alert(data._error_message);
        }
    })
    .catch(err => {
        alert("Error enrolling: " + err);
    });

    return false;
}
