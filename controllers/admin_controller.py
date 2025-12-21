from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import logging
from core.storage import repository
from core.services import notification_service

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)

def get_all_requests():
    """Read all requests from Repository and map to UI fields."""
    apps = repository.get_all_applications()
    mapped_rows = []
    
    # Pre-fetch all users to avoid N+1 lookups (optimization)
    users_list = repository.csv_store.read_all('users')
    users_map = {u['userid']: u.get('name', 'Unknown') for u in users_list}
    
    for app in apps:
        # Map fields to match admin.html expectations
        mapped_rows.append({
            "RequestID": app.get('appid'),
            "Citizen": users_map.get(app.get('userid'), "Unknown"),
            "Type": app.get('type'),
            "Status": app.get('status'),
            "userid": app.get('userid') # Keep for internal use if needed
        })
    return mapped_rows

def update_request_status(request_id, new_status):
    """Update request status in Repository and notify user."""
    # update_application_status returns the updated row or None
    updated_app = repository.update_application_status(str(request_id), new_status)
    
    if updated_app:
        # Determine notification type
        notif_code = None
        if new_status == "Approved":
            notif_code = "APP_APPROVE"
        elif new_status == "Rejected":
            notif_code = "APP_REJECT"
            
        if notif_code:
            notification_service.send_status_notification(updated_app['userid'], notif_code)
            logger.info(f"Notification {notif_code} sent to user {updated_app['userid']}")
    else:
        logger.warning(f"Request {request_id} not found for update")
        raise Exception("Request not found")

def filter_requests(filter_type):
    """Filter requests by status."""
    all_requests = get_all_requests()
    if filter_type == "pending":
        return [r for r in all_requests if r.get("Status") == "Pending"]
    elif filter_type == "in_process":
        return [r for r in all_requests if r.get("Status") == "In Process"]
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
