"""
Delivery Controller - Handles all delivery agent features
MVC Pattern: Controller layer for Delivery operations
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
import csv
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

delivery_bp = Blueprint("delivery", __name__)

# Get the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DELIVERIES_CSV = os.path.join(DATA_DIR, "deliveries.csv")
REQUESTS_CSV = os.path.join(DATA_DIR, "requests.csv")


def get_deliveries_for_agent(agent_id):
    """Get all deliveries assigned to a specific agent."""
    deliveries = []
    if not os.path.exists(DELIVERIES_CSV):
        return deliveries
    
    try:
        with open(DELIVERIES_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("AgentID", "").strip() == agent_id:
                    deliveries.append(row)
        logger.info(f"Found {len(deliveries)} deliveries for agent {agent_id}")
    except Exception as e:
        logger.error(f"Error reading deliveries CSV: {str(e)}")
    
    return deliveries


def update_delivery_status(delivery_id, new_status):
    """Update delivery status in CSV."""
    if not os.path.exists(DELIVERIES_CSV):
        logger.error(f"Deliveries CSV not found: {DELIVERIES_CSV}")
        return False
    
    rows = []
    try:
        with open(DELIVERIES_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        logger.error(f"Error reading deliveries CSV: {str(e)}")
        return False
    
    found = False
    for row in rows:
        if row.get("DeliveryID", "").strip() == str(delivery_id):
            row["Status"] = new_status
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if new_status == "Out for Delivery":
                row["OutForDeliveryAt"] = now
            elif new_status == "Delivered":
                row["DeliveredAt"] = now
                # Also update the request status
                update_request_status(row.get("RequestID", ""), "Delivered")
            elif new_status == "Failed":
                row["FailedAt"] = now
                # Also update the request status
                update_request_status(row.get("RequestID", ""), "Failed")
            
            found = True
            break
    
    if not found:
        logger.warning(f"Delivery {delivery_id} not found")
        return False
    
    # Write back to CSV
    if rows:
        fieldnames = rows[0].keys()
        try:
            with open(DELIVERIES_CSV, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            logger.info(f"Updated delivery {delivery_id} to status {new_status}")
            return True
        except Exception as e:
            logger.error(f"Error writing deliveries CSV: {str(e)}")
            return False
    
    return False


def update_request_status(request_id, new_status):
    """Update request status in requests.csv when delivery is completed."""
    if not os.path.exists(REQUESTS_CSV):
        return
    
    rows = []
    try:
        with open(REQUESTS_CSV, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        logger.error(f"Error reading requests CSV: {str(e)}")
        return
    
    for row in rows:
        rid = row.get("RequestID") or row.get("id")
        if rid == request_id:
            if "Status" in row:
                row["Status"] = new_status
            else:
                row["status"] = new_status
            break
    
    if rows:
        fieldnames = rows[0].keys()
        try:
            with open(REQUESTS_CSV, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        except Exception as e:
            logger.error(f"Error writing requests CSV: {str(e)}")


@delivery_bp.route("/delivery")
def delivery_dashboard():
    """Delivery agent dashboard showing assigned deliveries."""
    if 'user_id' not in session or not session.get('user_id'):
        flash('You must log in first', 'error')
        return redirect(url_for('login_page'))
    
    if session.get('role', '').upper() != 'DELIVERY':
        flash('Access denied. Delivery agent privileges required.', 'error')
        return redirect(url_for('login_page'))
    
    agent_id = session.get("user_id")
    deliveries = get_deliveries_for_agent(agent_id)
    
    return render_template("delivery_dashboard.html", deliveries=deliveries)


@delivery_bp.route("/delivery/update", methods=["POST"])
def update_delivery():
    """Update delivery status."""
    if 'user_id' not in session or not session.get('user_id'):
        flash('You must log in first', 'error')
        return redirect(url_for('login_page'))
    
    if session.get('role', '').upper() != 'DELIVERY':
        flash('Access denied. Delivery agent privileges required.', 'error')
        return redirect(url_for('login_page'))
    
    delivery_id = request.form.get("delivery_id")
    new_status = request.form.get("status")
    
    if not delivery_id or not new_status:
        flash("Missing delivery ID or status", "error")
        return redirect(url_for("delivery.delivery_dashboard"))
    
    # Validate status
    valid_statuses = ["Pending", "Out for Delivery", "Delivered", "Failed"]
    if new_status not in valid_statuses:
        flash(f"Invalid status: {new_status}", "error")
        return redirect(url_for("delivery.delivery_dashboard"))
    
    # Check if delivery is already completed
    deliveries = get_deliveries_for_agent(session.get("user_id"))
    for delivery in deliveries:
        if delivery.get("DeliveryID", "").strip() == str(delivery_id):
            current_status = delivery.get("Status", "").strip()
            if current_status in ["Delivered", "Failed"]:
                flash("Cannot update a completed delivery", "error")
                return redirect(url_for("delivery.delivery_dashboard"))
            break
    
    # Update the delivery
    if update_delivery_status(delivery_id, new_status):
        flash(f"Delivery {delivery_id} updated to {new_status}", "success")
    else:
        flash(f"Failed to update delivery {delivery_id}", "error")
    
    return redirect(url_for("delivery.delivery_dashboard"))
