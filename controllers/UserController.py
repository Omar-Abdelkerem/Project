from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import csv
import os

user_controller = Blueprint('user_controller', __name__)

# Get CSV path dynamically - go up 2 levels from controllers/UserController.py to get to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USERS_CSV = os.path.join(BASE_DIR, "data", "users.csv")


def _create_default_users_csv():
    """Create a default users CSV file with admin and delivery users."""
    import uuid
    os.makedirs(os.path.dirname(USERS_CSV), exist_ok=True)
    
    with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['user_id', 'national_id', 'name', 'email', 'phone', 'password_hash', 'role'])
        writer.writerow([str(uuid.uuid4()), '00000000000000', 'Admin User', 'admin@system.com', '01000000000', 'admin123', 'ADMIN'])
        writer.writerow([str(uuid.uuid4()), '11111111111111', 'Delivery Agent', 'agent@system.com', '01111111111', 'agent123', 'DELIVERY'])


@user_controller.route('/login', methods=['POST'])
def login():
    """Handle user login with CSV-based authentication."""
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    if not email or not password:
        flash('Email and password are required.', 'error')
        return redirect(url_for('login_page'))

    # Ensure CSV exists - create data directory if needed
    data_dir = os.path.dirname(USERS_CSV)
    os.makedirs(data_dir, exist_ok=True)
    
    # Read users from CSV - if it doesn't exist, create it with default users
    if not os.path.exists(USERS_CSV):
        _create_default_users_csv()
    
    # Verify CSV file exists and is readable
    if not os.path.exists(USERS_CSV):
        flash(f'User database not found at: {USERS_CSV}. Please contact administrator.', 'error')
        return redirect(url_for('login_page'))

    try:
        # Normalize input email to lowercase for comparison
        email_lower = email.lower().strip()
        password_stripped = password.strip()  # Remove any accidental whitespace
        
        found_email = False
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Get user data and normalize
                user_email = row.get('email', '').strip()
                user_email_lower = user_email.lower()
                user_password = row.get('password_hash', '').strip()
                user_role = row.get('role', '').strip().upper()
                user_id = row.get('user_id', '').strip()
                user_name = row.get('name', '').strip()

                # Check if email matches (case-insensitive)
                if user_email_lower == email_lower:
                    found_email = True
                    
                    # Compare password (exact match, case-sensitive)
                    if user_password == password_stripped:
                        # Set session
                        session['user_id'] = user_id
                        session['email'] = user_email
                        session['role'] = user_role
                        session['name'] = user_name
                        
                        # Ensure session is saved
                        session.permanent = True
                        
                        # Clear any previous error messages
                        if '_flashes' in session:
                            session.pop('_flashes', None)
                        
                        # Force session to save
                        from flask import session as flask_session
                        flask_session.modified = True

                        # Redirect based on role - MUST be inside the if block
                        if user_role == 'ADMIN':
                            flash(f'Welcome, {user_name}!', 'success')
                            return redirect(url_for('admin.admin_dashboard'))
                        elif user_role == 'DELIVERY':
                            flash(f'Welcome, {user_name}!', 'success')
                            return redirect(url_for('delivery.delivery_dashboard'))
                        elif user_role == 'CITIZEN':
                            flash(f'Welcome, {user_name}!', 'success')
                            return redirect(url_for('citizen.citizen_dashboard'))
                        else:
                            flash(f'Welcome, {user_name}!', 'success')
                            return redirect(url_for('user_controller.dashboard'))
                    else:
                        # Email found but password wrong
                        flash(f'Incorrect password for {email}. Please check your password.', 'error')
                        return redirect(url_for('login_page'))
        
        # Email not found
        if not found_email:
            flash(f'No account found with email: {email}. Please check your email or register.', 'error')
        else:
            flash('Invalid email or password. Please check your credentials and try again.', 'error')
            
    except Exception as e:
        import traceback
        error_msg = f'Error reading user database: {str(e)}'
        print(f"Login error: {error_msg}")
        print(traceback.format_exc())
        flash(error_msg + '. Please contact administrator.', 'error')
    
    return redirect(url_for('login_page'))


@user_controller.route('/dashboard')
def dashboard():
    """User dashboard for CITIZEN role."""
    if 'user_id' not in session:
        flash('Please login to access this page.', 'error')
        return redirect(url_for('login_page'))
    
    return render_template('dashboard.html', user=session)


@user_controller.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))
