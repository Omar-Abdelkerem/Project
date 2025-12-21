from flask import Blueprint, render_template, request, redirect, url_for, flash
import os
import csv
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__)

# Get the project root directory (go up 2 levels from controllers/admin_controller.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

CSV_PATH = os.path.join(DATA_DIR, "requests.csv")
DELIVERIES_CSV = os.path.join(DATA_DIR, "deliveries.csv")


def get_all_requests():
    rows = []
    try:
        if not os.path.exists(CSV_PATH):
            logger.warning(f"CSV file not found: {CSV_PATH}")
            return []
        
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            logger.info(f"Loaded {len(rows)} requests from {CSV_PATH}")
    except FileNotFoundError:
        logger.warning(f"CSV file not found: {CSV_PATH}")
        return []
    except Exception as e:
        logger.error(f"Error reading CSV: {str(e)}")
        return []
    return rows


def update_request_status(request_id, new_status):
    rows = []
    try:
        with open(CSV_PATH, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except FileNotFoundError:
        logger.error(f"CSV file not found: {CSV_PATH}")
        return

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


def create_delivery_if_not_exists(request_id):
    # Find first available delivery agent from users.csv
    agent_id = None
    users_csv = os.path.join(BASE_DIR, "data", "users.csv")
    
    if os.path.exists(users_csv):
        with open(users_csv, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('role', '').upper() == 'DELIVERY':
                    agent_id = row.get('user_id', '').strip()
                    break
    
    # Use default if no delivery agent found
    if not agent_id:
        agent_id = "agent1"
    
    if not os.path.exists(DELIVERIES_CSV):
        with open(DELIVERIES_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "DeliveryID",
                "RequestID",
                "AgentID",
                "Status",
                "OutForDeliveryAt",
                "DeliveredAt",
                "FailedAt"
            ])

    with open(DELIVERIES_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # Check if delivery already exists for this request
    for r in rows:
        if r.get("RequestID") == request_id:
            return

    # Generate unique delivery ID
    if rows:
        existing_ids = [int(r.get("DeliveryID", "0")) for r in rows if r.get("DeliveryID", "").isdigit()]
        delivery_id = str(max(existing_ids) + 1) if existing_ids else "1"
    else:
        delivery_id = "1"

    with open(DELIVERIES_CSV, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            delivery_id,
            request_id,
            agent_id,
            "Pending",
            "",
            "",
            ""
        ])


def filter_requests(filter_type):
    all_requests = get_all_requests()
    if filter_type == "pending":
        return [r for r in all_requests if (r.get("Status") or r.get("status")) == "Pending"]
    elif filter_type == "in_process":
        return [r for r in all_requests if (r.get("Status") or r.get("status")) == "In Process"]
    return all_requests


@admin_bp.route("/admin")
def admin_dashboard():
    from flask import session
    # Check if user is admin
    if session.get('role', '').upper() != 'ADMIN':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login_page'))
    
    requests_list = get_all_requests()
    logger.info(f"Rendering admin dashboard with {len(requests_list)} requests")
    return render_template("admin/admin.html", requests=requests_list)


@admin_bp.route("/admin/action", methods=["POST"])
def admin_action():
    from flask import session
    from controllers.citizen_controller import create_notification, log_audit_action
    
    # Check if user is admin
    if session.get('role', '').upper() != 'ADMIN':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login_page'))
    
    request_id = request.form.get("request_id")
    action = request.form.get("action")

    if not request_id or not action:
        flash("Invalid request.", "error")
        return redirect(url_for("admin.admin_dashboard"))

    try:
        # Get request details to find citizen
        requests_list = get_all_requests()
        request_data = None
        citizen_id = None
        for req in requests_list:
            if req.get("RequestID") == request_id:
                request_data = req
                citizen_id = req.get("CitizenID") or req.get("Citizen")
                break
        
        if action == "approve":
            update_request_status(request_id, "Approved")
            create_delivery_if_not_exists(request_id)
            
            # Create notification for citizen
            if citizen_id:
                tracking_id = request_data.get("TrackingID", request_id) if request_data else request_id
                create_notification(
                    citizen_id, 
                    request_id, 
                    f"Your National ID card application {tracking_id} has been approved! Delivery will be arranged soon.", 
                    'success'
                )
            
            # Log audit action
            log_audit_action(
                session.get('user_id'),
                'ADMIN',
                'APPROVE',
                'Request',
                request_id,
                f"Request approved and delivery created"
            )
            
            flash(f"Request {request_id} approved and delivery created.", "success")

        elif action == "reject":
            update_request_status(request_id, "Rejected")
            
            # Create notification for citizen
            if citizen_id:
                tracking_id = request_data.get("TrackingID", request_id) if request_data else request_id
                create_notification(
                    citizen_id,
                    request_id,
                    f"Your National ID card application {tracking_id} has been rejected. Please review your application and resubmit if needed.",
                    'error'
                )
            
            # Log audit action
            log_audit_action(
                session.get('user_id'),
                'ADMIN',
                'REJECT',
                'Request',
                request_id,
                "Request rejected"
            )
            
            flash(f"Request {request_id} rejected.", "success")

        else:
            flash("Unknown action.", "error")

    except Exception as e:
        logger.error(str(e))
        flash("Error processing request.", "error")

    return redirect(url_for("admin.admin_dashboard"))


@admin_bp.route("/admin/filter", methods=["POST"])
def admin_filter():
    from flask import session
    # Check if user is admin
    if session.get('role', '').upper() != 'ADMIN':
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login_page'))
    
    filter_type = request.form.get("filter", "all")
    requests_list = filter_requests(filter_type)
    return render_template("admin/admin.html", requests=requests_list, current_filter=filter_type)
