"""
Application Controller - Handles all citizen application routes
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import os
from datetime import datetime

from repositories.application_repository import ApplicationRepository
from models.application import Application

# Create Blueprint
application_bp = Blueprint('application', __name__)

# Initialize repository
app_repo = ApplicationRepository()

# File upload configuration
UPLOAD_FOLDER = 'static/uploads/documents'
ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """
    Check if file extension is allowed
    
    Args:
        filename: Name of the file
        
    Returns:
        bool: True if extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def check_file_size(file):
    """
    Check if file size is within limit
    
    Args:
        file: File object from request
        
    Returns:
        bool: True if size is acceptable
    """
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    return file_size <= MAX_FILE_SIZE


@application_bp.route('/citizen/dashboard')
def citizen_dashboard():
    """
    Citizen dashboard - shows all user's applications
    """
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login_page'))
    
    # Check if user is citizen (not admin)
    if session.get('user_role') == 'admin':
        flash('This page is for citizens only', 'error')
        return redirect(url_for('admin.admin_dashboard'))
    
    user_id = session['user_id']
    user_name = session.get('user_name', 'User')
    
    # Get all applications for this user
    applications = app_repo.get_by_user_id(user_id)
    
    # Sort by created_at (newest first)
    applications.sort(key=lambda x: x.created_at if x.created_at else '', reverse=True)
    
    return render_template('citizen_dashboard.html',
                          user_name=user_name,
                          applications=applications)


@application_bp.route('/citizen/apply', methods=['GET', 'POST'])
def submit_application():
    """
    Submit new application form
    """
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login_page'))
    
    if request.method == 'GET':
        return render_template('apply.html', errors=[])
    
    # POST - Handle form submission
    user_id = session['user_id']
    user_name = session['user_name']
    
    # Get form data
    application_type = request.form.get('application_type', '').strip()
    description = request.form.get('description', '').strip()
    
    # Validation
    errors = []
    if not application_type:
        errors.append('Application type is required')
    if not description or len(description) < 10:
        errors.append('Description must be at least 10 characters')
    
    # Handle file upload
    document_path = None
    if 'document' in request.files:
        file = request.files['document']
        
        if file.filename != '':  # File was selected
            # Check file extension
            if not allowed_file(file.filename):
                errors.append('Invalid file type. Only PDF, JPG, JPEG, PNG are allowed')
            
            # Check file size
            elif not check_file_size(file):
                errors.append('File size must be less than 5MB')
            
            else:
                # Save file
                filename = secure_filename(file.filename)
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{user_id}_{timestamp}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                
                try:
                    file.save(file_path)
                    document_path = file_path
                except Exception as e:
                    errors.append(f'Error uploading file: {str(e)}')
    
    # If there are errors, show form again
    if errors:
        return render_template('apply.html', 
                             errors=errors,
                             application_type=application_type,
                             description=description)
    
    # Generate tracking ID
    tracking_id = app_repo.generate_tracking_id()
    
    # Create application object
    application = Application(
        tracking_id=tracking_id,
        user_id=user_id,
        user_name=user_name,
        application_type=application_type,
        description=description,
        status='Pending',
        document_path=document_path,
        created_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        updated_at=None,
        notes=None
    )
    
    # Save to repository
    if app_repo.save(application):
        flash(f'Application submitted successfully! Your tracking ID is: {tracking_id}', 'success')
        return redirect(url_for('application.citizen_dashboard'))
    else:
        flash('Error submitting application. Please try again.', 'error')
        return render_template('apply.html', 
                             errors=['System error. Please try again.'],
                             application_type=application_type,
                             description=description)


@application_bp.route('/citizen/track', methods=['GET', 'POST'])
def track_application():
    """
    Track application status by tracking ID
    """
    if request.method == 'GET':
        return render_template('track.html', application=None)
    
    # POST - Search for application
    tracking_id = request.form.get('tracking_id', '').strip()
    
    if not tracking_id:
        flash('Please enter a tracking ID', 'error')
        return render_template('track.html', application=None)
    
    # Search for application
    application = app_repo.get_by_tracking_id(tracking_id)
    
    if not application:
        flash(f'No application found with tracking ID: {tracking_id}', 'error')
        return render_template('track.html', application=None)
    
    # Check if logged in user owns this application (optional security)
    if 'user_id' in session:
        if application.user_id != session['user_id'] and session.get('user_role') != 'admin':
            flash('You do not have permission to view this application', 'error')
            return render_template('track.html', application=None)
    
    return render_template('track.html', application=application)


@application_bp.route('/citizen/application/<tracking_id>')
def view_application_details(tracking_id):
    """
    View detailed information about a specific application
    """
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please login first', 'error')
        return redirect(url_for('login_page'))
    
    # Get application
    application = app_repo.get_by_tracking_id(tracking_id)
    
    if not application:
        flash('Application not found', 'error')
        return redirect(url_for('application.citizen_dashboard'))
    
    # Check if user owns this application
    if application.user_id != session['user_id'] and session.get('user_role') != 'admin':
        flash('You do not have permission to view this application', 'error')
        return redirect(url_for('application.citizen_dashboard'))
    
    return render_template('application_details.html', application=application)