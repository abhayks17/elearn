import frappe
import requests

@frappe.whitelist()
def check_plagiarism(submission_name):
    submission = frappe.get_doc("Assignment Submission", submission_name)
    text = submission.submission_text

    if not text or len(text.strip()) < 100:
        frappe.throw("Submission text must be at least 100 characters.")

    url = "https://api.gowinston.ai/v2/plagiarism"
    headers = {
        "Authorization": "Bearer PzSiYsppWueCerewazwI2ATP6W5DBdyIoi8ktvika720d9ec",
        "Content-Type": "application/json"
    }

    payload = {
        "text": text.strip(),
        "language": "en",
        "country": "us"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        return {
            "similarity": result.get("result", {}).get("score"),
            "sources": result.get("result", {}).get("sources", [])
        }

    except requests.exceptions.RequestException as e:
        frappe.log_error(frappe.get_traceback(), "Plagiarism Check Failed")
        frappe.throw("Failed to check plagiarism. Please try again.")
