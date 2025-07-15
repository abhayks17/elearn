# elearn/api/handler.py
import frappe
from frappe.handler import execute_cmd

def handle():
    if frappe.request.path == "/api/method/elearn.api.assignment_submission.grade_submission":
        frappe.local.flags.ignore_csrf = True  # ✅ disable CSRF for this specific call

    return execute_cmd(frappe.form_dict.cmd)
