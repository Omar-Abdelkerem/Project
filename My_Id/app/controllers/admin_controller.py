from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import csv

admin_bp = Blueprint("admin", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "app", "data", "requests.csv")

def get_all_requests():
    """Read all requests from CSV."""
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows

def update_request_status(request_id, new_status):
    """Update request status in CSV."""
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        rid = row.get("RequestID") or row.get("id")
        if rid == request_id:
            if "Status" in row:
                row["Status"] = new_status
            else:
                row["status"] = new_status
            break

    if not rows:
        return
    fieldnames = rows[0].keys()
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def filter_requests(filter_type):
    """Filter requests by status."""
    all_requests = get_all_requests()
    if filter_type == "pending":
        return [r for r in all_requests if (r.get("Status") or r.get("status")) == "Pending"]
    elif filter_type == "in_process":
        return [r for r in all_requests if (r.get("Status") or r.get("status")) == "In Process"]
    else:
        return all_requests

@admin_bp.route("/admin")
def admin_dashboard():
    """Display all requests."""
    requests_list = get_all_requests()
    return render_template("admin/admin.html", requests=requests_list)

@admin_bp.route("/admin/action", methods=["POST"])
def admin_action():
    """Handle Approve/Reject button clicks."""
    request_id = request.form.get("request_id")
    action = request.form.get("action")

    print(f"DEBUG: Received request_id={request_id}, action={action}")

    if action == "approve":
        update_request_status(request_id, "Approved")
        print(f"DEBUG: Updated {request_id} to Approved")
        flash(f"Request {request_id} approved.", "success")
    elif action == "reject":
        update_request_status(request_id, "Rejected")
        print(f"DEBUG: Updated {request_id} to Rejected")
        flash(f"Request {request_id} rejected.", "warning")

    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/admin/filter", methods=["POST"])
def admin_filter():
    """Handle filter button clicks."""
    filter_type = request.form.get("filter")

    print(f"DEBUG: Filter type = {filter_type}")

    requests_list = filter_requests(filter_type)
    return render_template("admin/admin.html", requests=requests_list)
