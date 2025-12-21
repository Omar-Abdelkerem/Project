from flask import Blueprint, render_template, request, redirect, url_for, flash
import csv
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

delivery_bp = Blueprint("delivery", __name__)

# Get the project root directory (go up 2 levels from controllers/delivery_controller.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DELIVERY_CSV = os.path.join(BASE_DIR, "data", "deliveries.csv")
REQUESTS_CSV = os.path.join(BASE_DIR, "data", "requests.csv")

# =========================
# Helper functions
# =========================

def read_deliveries():
    if not os.path.exists(DELIVERY_CSV):
        logger.warning(f"Deliveries CSV not found: {DELIVERY_CSV}")
        return []
    try:
        with open(DELIVERY_CSV, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            logger.info(f"Read {len(rows)} deliveries from CSV")
            return rows
    except Exception as e:
        logger.error(f"Error reading deliveries CSV: {str(e)}")
        return []

def write_deliveries(rows):
    if not rows:
        logger.warning("No rows to write to deliveries CSV")
        return
    
    try:
        # Ensure all rows have the same keys
        fieldnames = ['DeliveryID', 'RequestID', 'AgentID', 'Status', 'OutForDeliveryAt', 'DeliveredAt', 'FailedAt']
        
        with open(DELIVERY_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write rows, ensuring all fields are present
            for row in rows:
                # Create a new dict with all required fields
                clean_row = {field: row.get(field, '') for field in fieldnames}
                writer.writerow(clean_row)
        
        logger.info(f"Successfully wrote {len(rows)} deliveries to {DELIVERY_CSV}")
    except Exception as e:
        logger.error(f"Error writing deliveries CSV: {str(e)}")
        raise

def sync_request_status(delivery):
    """Update the related Request status based on Delivery status."""
    request_id = delivery["RequestID"]
    status_map = {"Delivered": "Completed", "Failed": "Failed"}

    if delivery["Status"] not in status_map:
        return

    # اقرأ Requests CSV
    rows = []
    with open(REQUESTS_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    # حدث حالة الطلب
    for r in rows:
        if r["RequestID"] == request_id:
            r["Status"] = status_map[delivery["Status"]]
            break

    # اكتب مرة تانية
    with open(REQUESTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

# =========================
# Delivery Dashboard
# =========================

@delivery_bp.route("/delivery")
def delivery_dashboard():
    from flask import session
    # Check if user is delivery agent
    if session.get('role', '').upper() != 'DELIVERY':
        flash('Access denied. Delivery agent privileges required.', 'error')
        return redirect(url_for('login_page'))
    
    # Get agent ID from session
    agent_id = session.get('user_id', 'agent1')
    deliveries = read_deliveries()
    agent_deliveries = [d for d in deliveries if d.get("AgentID") == agent_id]
    return render_template(
        "delivery_dashboard.html",
        deliveries=agent_deliveries
    )

# =========================
# Update Delivery Status
# =========================

@delivery_bp.route("/delivery/update", methods=["POST"])
def update_delivery_status():
    from flask import session
    # Check if user is delivery agent
    if session.get('role', '').upper() != 'DELIVERY':
        flash('Access denied. Delivery agent privileges required.', 'error')
        return redirect(url_for('login_page'))
    
    # Get form data - check both form.get and request.values
    delivery_id = request.form.get("delivery_id") or request.values.get("delivery_id")
    new_status = request.form.get("status") or request.values.get("status")
    
    # Also check if it came as JSON
    if not delivery_id or not new_status:
        try:
            data = request.get_json()
            if data:
                delivery_id = data.get("delivery_id") or delivery_id
                new_status = data.get("status") or new_status
        except:
            pass

    # Debug: log all form data
    logger.info(f"Form data: {dict(request.form)}")
    logger.info(f"All values: {dict(request.values)}")
    logger.info(f"Update request: delivery_id={delivery_id}, new_status={new_status}")

    if not delivery_id or not new_status:
        flash(f"Invalid request parameters. Received: delivery_id={delivery_id}, status={new_status}", "error")
        logger.warning(f"Missing parameters - delivery_id: {delivery_id}, new_status: {new_status}")
        logger.warning(f"Available form keys: {list(request.form.keys())}")
        return redirect(url_for("delivery.delivery_dashboard"))

    try:
        deliveries = read_deliveries()
        logger.info(f"Read {len(deliveries)} deliveries from CSV")
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        agent_id = session.get('user_id', 'agent1')
        logger.info(f"Agent ID from session: {agent_id}")
        
        delivery_found = False
        for d in deliveries:
            # Compare as strings to avoid type issues
            if str(d.get("DeliveryID", "")).strip() == str(delivery_id).strip():
                delivery_found = True
                logger.info(f"Found delivery: {d}")
                
                # Check if delivery is assigned to this agent
                delivery_agent_id = str(d.get("AgentID", "")).strip()
                if delivery_agent_id != str(agent_id).strip():
                    flash(f"You are not authorized to update this delivery. (AgentID: {delivery_agent_id}, Your ID: {agent_id})", "error")
                    logger.warning(f"Agent ID mismatch: {delivery_agent_id} != {agent_id}")
                    return redirect(url_for("delivery.delivery_dashboard"))

                # ===== rules =====
                current_status = d.get("Status", "").strip()
                logger.info(f"Current status: '{current_status}', New status: '{new_status}'")
                
                if current_status == "Delivered" or current_status == "Failed":
                    flash("Cannot change final status (Delivered/Failed).", "error")
                    return redirect(url_for("delivery.delivery_dashboard"))

                # Update status and timestamp
                if new_status == "Out for Delivery":
                    d["Status"] = new_status
                    d["OutForDeliveryAt"] = now
                    d["DeliveredAt"] = d.get("DeliveredAt", "")
                    d["FailedAt"] = d.get("FailedAt", "")
                    flash(f"Delivery {delivery_id} is now Out for Delivery.", "success")
                    logger.info(f"Updated delivery {delivery_id} to 'Out for Delivery'")

                elif new_status == "Delivered":
                    d["Status"] = new_status
                    d["DeliveredAt"] = now
                    d["FailedAt"] = d.get("FailedAt", "")
                    flash(f"Delivery {delivery_id} marked as Delivered.", "success")
                    logger.info(f"Updated delivery {delivery_id} to 'Delivered'")

                elif new_status == "Failed":
                    d["Status"] = new_status
                    d["FailedAt"] = now
                    d["DeliveredAt"] = d.get("DeliveredAt", "")
                    flash(f"Delivery {delivery_id} marked as Failed.", "success")
                    logger.info(f"Updated delivery {delivery_id} to 'Failed'")
                else:
                    flash(f"Invalid status: {new_status}.", "error")
                    logger.warning(f"Invalid status received: {new_status}")
                    return redirect(url_for("delivery.delivery_dashboard"))

            # ===== Sync with Request status =====
            try:
                sync_request_status(d)
                
                # Create notification for citizen
                from controllers.citizen_controller import create_notification, log_audit_action
                
                # Get citizen ID from request
                request_id = d.get("RequestID")
                citizen_id = None
                tracking_id = request_id
                
                if os.path.exists(REQUESTS_CSV):
                    with open(REQUESTS_CSV, 'r', newline='', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for req in reader:
                            if req.get("RequestID") == request_id:
                                citizen_id = req.get("CitizenID") or req.get("Citizen")
                                tracking_id = req.get("TrackingID", request_id)
                                break
                
                # Create notification
                if citizen_id:
                    if new_status == "Delivered":
                        create_notification(
                            citizen_id,
                            request_id,
                            f"Your National ID card for application {tracking_id} has been delivered successfully!",
                            'success'
                        )
                    elif new_status == "Failed":
                        create_notification(
                            citizen_id,
                            request_id,
                            f"Delivery failed for your National ID card application {tracking_id}. Please contact support.",
                            'error'
                        )
                    elif new_status == "Out for Delivery":
                        create_notification(
                            citizen_id,
                            request_id,
                            f"Your National ID card for application {tracking_id} is now out for delivery.",
                            'info'
                        )
                
                # Log audit action
                log_audit_action(
                    agent_id,
                    'DELIVERY',
                    'UPDATE_STATUS',
                    'Delivery',
                    delivery_id,
                    f"Status changed to {new_status}"
                )
                
            except Exception as e:
                logger.error(f"Error syncing request status: {str(e)}")
                # Don't fail the whole operation if sync fails
                
            break

        if not delivery_found:
            flash(f"Delivery {delivery_id} not found.", "error")
            logger.warning(f"Delivery {delivery_id} not found in {len(deliveries)} deliveries")
            return redirect(url_for("delivery.delivery_dashboard"))

        # Write the updated deliveries back to CSV
        write_deliveries(deliveries)
        logger.info("Successfully updated and saved deliveries")
        
    except Exception as e:
        logger.error(f"Error updating delivery status: {str(e)}", exc_info=True)
        flash(f"Error updating delivery: {str(e)}", "error")
    
    return redirect(url_for("delivery.delivery_dashboard"))
