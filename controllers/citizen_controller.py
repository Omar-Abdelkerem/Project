"""
Citizen Controller - Handles all citizen-related features
MVC Pattern: Controller layer for Citizen operations
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_from_directory
import csv
import os
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

citizen_bp = Blueprint("citizen", __name__)

# Get project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
REQUESTS_CSV = os.path.join(DATA_DIR, "requests.csv")
NOTIFICATIONS_CSV = os.path.join(DATA_DIR, "notifications.csv")
AUDIT_LOG_CSV = os.path.join(DATA_DIR, "audit_log.csv")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def init_notifications_csv():
    """Initialize notifications.csv if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(NOTIFICATIONS_CSV):
        with open(NOTIFICATIONS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['NotificationID', 'UserID', 'RequestID', 'Message', 'Type', 'Read', 'CreatedAt'])


def init_audit_log_csv():
    """Initialize audit_log.csv if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(AUDIT_LOG_CSV):
        with open(AUDIT_LOG_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['LogID', 'Timestamp', 'ActorID', 'ActorRole', 'Action', 'EntityType', 'EntityID', 'Details'])


def create_notification(user_id, request_id, message, notification_type='info'):
    """Create a notification for a user."""
    init_notifications_csv()
    
    notification_id = str(uuid.uuid4())
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(NOTIFICATIONS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            notification_id,
            user_id,
            request_id,
            message,
            notification_type,
            'False',
            created_at
        ])
    
    logger.info(f"Created notification {notification_id} for user {user_id}")


def log_audit_action(actor_id, actor_role, action, entity_type, entity_id, details=''):
    """Log an audit action."""
    init_audit_log_csv()
    
    log_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(AUDIT_LOG_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            log_id,
            timestamp,
            actor_id,
            actor_role,
            action,
            entity_type,
            entity_id,
            details
        ])
    
    logger.info(f"Audit log: {actor_role} {actor_id} performed {action} on {entity_type} {entity_id}")


def generate_tracking_id():
    """Generate a unique tracking ID."""
    return f"TRK-{uuid.uuid4().hex[:8].upper()}"


def get_user_requests(user_id):
    """Get all requests for a specific user."""
    if not os.path.exists(REQUESTS_CSV):
        return []
    
    user_requests = []
    with open(REQUESTS_CSV, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Match by user_id if CitizenID column exists, or by name if Citizen column
            if 'CitizenID' in row and row.get('CitizenID') == user_id:
                user_requests.append(row)
            elif 'Citizen' in row:
                # For backward compatibility, we'll match by name
                # In production, always use CitizenID
                pass
    
    return user_requests


def get_request_status_history(request_id):
    """Get status history for a request (from audit log)."""
    history = []
    if os.path.exists(AUDIT_LOG_CSV):
        with open(AUDIT_LOG_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('EntityType') == 'Request' and row.get('EntityID') == request_id:
                    history.append({
                        'timestamp': row.get('Timestamp'),
                        'action': row.get('Action'),
                        'actor': row.get('ActorRole'),
                        'details': row.get('Details')
                    })
    
    return sorted(history, key=lambda x: x['timestamp'], reverse=True)


@citizen_bp.route('/citizen/dashboard')
def citizen_dashboard():
    """Citizen dashboard showing all their applications."""
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login_page'))
    
    if session.get('role', '').upper() != 'CITIZEN':
        flash('Access denied. Citizen privileges required.', 'error')
        return redirect(url_for('login_page'))
    
    user_id = session.get('user_id')
    
    # Get user's requests
    requests = get_user_requests(user_id)
    
    # Get unread notifications
    notifications = []
    if os.path.exists(NOTIFICATIONS_CSV):
        with open(NOTIFICATIONS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('UserID') == user_id and row.get('Read', 'False').lower() == 'false':
                    notifications.append(row)
    
    return render_template('citizen/dashboard.html', 
                         requests=requests, 
                         notifications=notifications,
                         user=session)


@citizen_bp.route('/citizen/apply', methods=['GET', 'POST'])
def apply():
    """Application submission form."""
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login_page'))
    
    if session.get('role', '').upper() != 'CITIZEN':
        flash('Access denied. Citizen privileges required.', 'error')
        return redirect(url_for('login_page'))
    
    if request.method == 'GET':
        return render_template('citizen/apply.html')
    
    # Handle POST - submit application
    application_type = request.form.get('type', '').strip()
    description = request.form.get('description', '').strip()
    uploaded_file = request.files.get('document')
    
    errors = []
    
    if not application_type:
        errors.append('Application type is required')
    
    if not description:
        errors.append('Additional information is required')
    
    # Document is optional per SRS, but recommended
    # if not uploaded_file or not uploaded_file.filename:
    #     errors.append('Document upload is required')
    
    if errors:
        return render_template('citizen/apply.html', errors=errors, 
                             type=application_type, description=description)
    
    # Generate unique tracking ID
    tracking_id = generate_tracking_id()
    request_id = f"R-{uuid.uuid4().hex[:6].upper()}"
    user_id = session.get('user_id')
    user_name = session.get('name', 'Unknown')
    
    # Handle file upload
    file_path = ''
    if uploaded_file and uploaded_file.filename:
        if not allowed_file(uploaded_file.filename):
            errors.append('Invalid file type. Only PDF, JPG, PNG allowed.')
            return render_template('citizen/apply.html', errors=errors,
                                 type=application_type, description=description)
        
        # Check file size
        uploaded_file.seek(0, os.SEEK_END)
        file_size = uploaded_file.tell()
        uploaded_file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            errors.append('File size exceeds 5MB limit.')
            return render_template('citizen/apply.html', errors=errors,
                                 type=application_type, description=description)
        
        # Save file
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_extension = uploaded_file.filename.rsplit('.', 1)[1].lower()
        file_path = f"{tracking_id}.{file_extension}"
        full_path = os.path.join(UPLOAD_FOLDER, file_path)
        uploaded_file.save(full_path)
    
    # Save application to requests.csv
    os.makedirs(DATA_DIR, exist_ok=True)
    file_exists = os.path.exists(REQUESTS_CSV)
    
    with open(REQUESTS_CSV, 'a', newline='', encoding='utf-8') as f:
        fieldnames = ['RequestID', 'TrackingID', 'CitizenID', 'Citizen', 'Type', 'Status', 'Description', 'DocumentPath', 'CreatedAt']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow({
            'RequestID': request_id,
            'TrackingID': tracking_id,
            'CitizenID': user_id,
            'Citizen': user_name,
            'Type': application_type,
            'Status': 'Pending',
            'Description': description,
            'DocumentPath': file_path,
            'CreatedAt': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    # Create notification
    create_notification(user_id, request_id, 
                       f"Your National ID card application {tracking_id} has been submitted successfully and is pending review.", 
                       'success')
    
    # Log audit action
    log_audit_action(user_id, 'CITIZEN', 'SUBMIT_APPLICATION', 'Request', request_id, 
                    f"National ID card application type: {application_type}")
    
    flash(f'National ID card application submitted successfully! Your Tracking ID: {tracking_id}. You will receive updates via notifications.', 'success')
    return redirect(url_for('citizen.citizen_dashboard'))


@citizen_bp.route('/citizen/track', methods=['GET', 'POST'])
def track():
    """Track application by Tracking ID."""
    if request.method == 'POST':
        tracking_id = request.form.get('tracking_id', '').strip().upper()
        
        if not tracking_id:
            flash('Please enter a Tracking ID', 'error')
            return render_template('citizen/track.html')
        
        # Find request by tracking ID
        request_data = None
        if os.path.exists(REQUESTS_CSV):
            with open(REQUESTS_CSV, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('TrackingID', '').upper() == tracking_id:
                        request_data = row
                        break
        
        if not request_data:
            flash(f'No application found with Tracking ID: {tracking_id}', 'error')
            return render_template('citizen/track.html')
        
        # Get status history
        status_history = get_request_status_history(request_data.get('RequestID'))
        
        return render_template('citizen/track.html', 
                             request=request_data, 
                             status_history=status_history,
                             tracking_id=tracking_id)
    
    return render_template('citizen/track.html')


@citizen_bp.route('/citizen/notifications')
def notifications():
    """View all notifications."""
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login_page'))
    
    user_id = session.get('user_id')
    all_notifications = []
    
    if os.path.exists(NOTIFICATIONS_CSV):
        with open(NOTIFICATIONS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('UserID') == user_id:
                    all_notifications.append(row)
    
    # Sort by date (newest first)
    all_notifications.sort(key=lambda x: x.get('CreatedAt', ''), reverse=True)
    
    return render_template('citizen/notifications.html', notifications=all_notifications)


@citizen_bp.route('/citizen/notifications/<notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session.get('user_id')
    
    if os.path.exists(NOTIFICATIONS_CSV):
        notifications = []
        with open(NOTIFICATIONS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames
            for row in reader:
                if row.get('NotificationID') == notification_id and row.get('UserID') == user_id:
                    row['Read'] = 'True'
                notifications.append(row)
        
        # Write back
        with open(NOTIFICATIONS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(notifications)
    
    return redirect(url_for('citizen.notifications'))


@citizen_bp.route('/citizen/download/<filename>')
def download_document(filename):
    """Download uploaded document."""
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login_page'))
    
    # Security: Only allow downloads from uploads folder
    return send_from_directory(UPLOAD_FOLDER, filename)
