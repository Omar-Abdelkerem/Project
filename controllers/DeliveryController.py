from flask import Blueprint, request, jsonify
from core.storage import repository
from core.services import notification_service

delivery_bp = Blueprint('delivery_bp', __name__)

@delivery_bp.route('/delivery/update', methods=['POST'])
def update_status():
    deliveryid = request.form.get('deliveryid')
    new_status = request.form.get('status') # e.g., "Out for Delivery", "Delivered"
    
    if not deliveryid or not new_status:
        return "Missing data", 400
        
    # Update status
    updated = repository.update_delivery_status(deliveryid, new_status)
    if not updated:
        return "Delivery not found", 404
        
    # Determine notification code
    # "Out for Delivery" -> DEL_OUT
    # "Delivered" -> DEL_DONE
    notif_code = None
    if "out" in new_status.lower():
        notif_code = "DEL_OUT"
    elif "delivered" in new_status.lower():
        notif_code = "DEL_DONE"
        
    if notif_code:
        # We need userid to send notification. Link is delivery -> app -> user
        app = repository.get_application_by_id(updated['appid'])
        if app:
            notification_service.send_status_notification(app['userid'], notif_code)
            
    return "Status updated", 200
