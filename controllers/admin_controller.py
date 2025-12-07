from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import csv
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "requests.csv")

def get_all_requests():
    """Read all requests from CSV."""
    rows = []
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        logger.warning(f"CSV file not found: {CSV_PATH}, returning empty list")
        return []
    except Exception as e:
        logger.error(f"Error reading CSV file: {str(e)}")
        return []
    return rows

def update_request_status(request_id, new_status):
    """Update request status in CSV."""
    rows = []
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        logger.error(f"CSV file not found: {CSV_PATH}")
        raise

    found = False
    for row in rows:
        rid = row.get("RequestID") or row.get("id")
        if rid == request_id:
            if "Status" in row:
                row["Status"] = new_status
            else:
                row["status"] = new_status
            found = True
            break

    if not found:
        logger.warning(f"Request {request_id} not found in CSV")

    if not rows:
        logger.warning("CSV is empty, nothing to write")
        return

    fieldnames = rows[0].keys()
    try:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        logger.debug(f"CSV file written successfully with {len(rows)} rows")
    except IOError as e:
        logger.error(f"Failed to write CSV: {str(e)}")
        raise

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

    if not request_id or not action:
        logger.warning("Missing request_id or action in form data")
        flash("Invalid request ID or action.", "error")
        return redirect(url_for("admin.admin_dashboard"))

    if action not in ["approve", "reject"]:
        logger.warning(f"Unknown action: {action}")
        flash(f"Unknown action: {action}", "error")
        return redirect(url_for("admin.admin_dashboard"))

    logger.info(f"Processing {action} for request_id={request_id}")

    try:
        new_status = "Approved" if action == "approve" else "Rejected"
        update_request_status(request_id, new_status)
        logger.info(f"Successfully updated {request_id} to {new_status}")
        flash(f"Request {request_id} {action}d successfully.", "success")
    except Exception as e:
        logger.error(f"Failed to update {request_id}: {str(e)}")
        flash(f"Error processing request: {str(e)}", "error")

    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/admin/filter", methods=["POST"])
def admin_filter():
    """Handle filter button clicks."""
    filter_type = request.form.get("filter")

    print(f"DEBUG: Filter type = {filter_type}")

    requests_list = filter_requests(filter_type)
    return render_template("admin/admin.html", requests=requests_list)
