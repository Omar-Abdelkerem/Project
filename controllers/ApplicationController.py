from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from core.storage import repository
from core.services import notification_service

application_bp = Blueprint('application_bp', __name__)

@application_bp.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'GET':
        # Simple form for application
        return render_template('apply.html') # Assuming template exists or we return text for now
    
    # POST
    # In a real app, we get userid from session. For now, we simulate or get from form.
    userid = request.form.get('userid')
    type = request.form.get('type')
    subtype = request.form.get('subtype')
    
    if not userid:
        return "User ID required", 400
        
    app = repository.create_application(userid, type, subtype, "Pending")
    
    # Send Notification
    notification_service.send_status_notification(userid, "APP_SUBMIT")
    
    return redirect(url_for('user_controller.dashboard'))
