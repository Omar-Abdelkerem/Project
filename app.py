from flask import Flask, render_template, request, session, redirect, url_for, flash
import csv
import uuid
import os
from controllers.UserController import user_controller
from controllers.admin_controller import admin_bp
from controllers.delivery_controller import delivery_bp
from controllers.citizen_controller import citizen_bp

# Get the base directory dynamically
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_CSV = os.path.join(DATA_DIR, "users.csv")
REQUESTS_CSV = os.path.join(DATA_DIR, "requests.csv")
DELIVERIES_CSV = os.path.join(DATA_DIR, "deliveries.csv")

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-change-me-in-production")
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# Register blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(user_controller)
app.register_blueprint(delivery_bp)
app.register_blueprint(citizen_bp)


# Make ensure_admin_delivery_users available globally
def get_users_csv_path():
    """Get the users CSV path - can be imported by other modules."""
    return USERS_CSV


def ensure_admin_delivery_users():
    """Ensure admin and delivery users exist with correct credentials."""
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Create users.csv with headers if it doesn't exist
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'user_id',
                'national_id',
                'name',
                'email',
                'phone',
                'password_hash',
                'role'
            ])
    
    # Read existing users
    existing_users = []
    admin_exists = False
    delivery_exists = False
    admin_user_id = None
    delivery_user_id = None
    
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = row.get('email', '').strip().lower()
                role = row.get('role', '').strip().upper()
                
                if email == 'admin@system.com':
                    admin_exists = True
                    admin_user_id = row.get('user_id', '').strip()
                elif email == 'agent@system.com':
                    delivery_exists = True
                    delivery_user_id = row.get('user_id', '').strip()
                
                existing_users.append(row)
    
    # Update or create admin user
    if admin_exists:
        # Update existing admin user to ensure correct password
        updated_users = []
        for row in existing_users:
            if row.get('email', '').strip().lower() == 'admin@system.com':
                row['password_hash'] = 'admin123'
                row['role'] = 'ADMIN'
                row['name'] = 'Admin User'
                row['national_id'] = '00000000000000'
                row['phone'] = '01000000000'
            updated_users.append(row)
        existing_users = updated_users
    else:
        # Add new admin user
        admin_user_id = str(uuid.uuid4())
        existing_users.append({
            'user_id': admin_user_id,
            'national_id': '00000000000000',
            'name': 'Admin User',
            'email': 'admin@system.com',
            'phone': '01000000000',
            'password_hash': 'admin123',
            'role': 'ADMIN'
        })
    
    # Update or create delivery user
    if delivery_exists:
        # Update existing delivery user to ensure correct password
        updated_users = []
        for row in existing_users:
            if row.get('email', '').strip().lower() == 'agent@system.com':
                row['password_hash'] = 'agent123'
                row['role'] = 'DELIVERY'
                row['name'] = 'Delivery Agent'
                row['national_id'] = '11111111111111'
                row['phone'] = '01111111111'
            updated_users.append(row)
        existing_users = updated_users
    else:
        # Add new delivery user
        delivery_user_id = str(uuid.uuid4())
        existing_users.append({
            'user_id': delivery_user_id,
            'national_id': '11111111111111',
            'name': 'Delivery Agent',
            'email': 'agent@system.com',
            'phone': '01111111111',
            'password_hash': 'agent123',
            'role': 'DELIVERY'
        })
    
    # Write all users back to CSV
    fieldnames = ['user_id', 'national_id', 'name', 'email', 'phone', 'password_hash', 'role']
    with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(existing_users)


def init_requests_csv():
    """Initialize requests.csv with headers if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(REQUESTS_CSV):
        with open(REQUESTS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['RequestID', 'Citizen', 'Type', 'Status'])


def init_deliveries_csv():
    """Initialize deliveries.csv with headers if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DELIVERIES_CSV):
        with open(DELIVERIES_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'DeliveryID',
                'RequestID',
                'AgentID',
                'Status',
                'OutForDeliveryAt',
                'DeliveredAt',
                'FailedAt'
            ])


@app.route('/')
def index():
    """Home page route."""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route."""
    if request.method == 'GET':
        return render_template('register.html', errors=[])

    name = request.form.get('name', '').strip()
    national_id = request.form.get('national_id', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '')
    confirm = request.form.get('confirm_password', '')

    errors = []

    if not name:
        errors.append('Name is required')

    if len(national_id) != 14 or not national_id.isdigit():
        errors.append('National ID must be 14 digits')

    if not email:
        errors.append('Email is required')

    if not phone:
        errors.append('Phone is required')

    if not password:
        errors.append('Password is required')

    if password != confirm:
        errors.append('Passwords do not match')

    if errors:
        return render_template(
            'register.html',
            errors=errors,
            name=name,
            national_id=national_id,
            email=email,
            phone=phone
        )

    # Check if email already exists
    if os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('email', '').strip().lower() == email.lower():
                    errors.append('Email already registered')
                    return render_template(
                        'register.html',
                        errors=errors,
                        name=name,
                        national_id=national_id,
                        email=email,
                        phone=phone
                    )

    user_id = str(uuid.uuid4())
    password_hash = password  # In production, use proper password hashing

    ensure_admin_delivery_users()  # Ensure CSV exists

    # Write user to CSV
    file_exists = os.path.exists(USERS_CSV)
    with open(USERS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        # Only write header if file is new
        if not file_exists:
            writer.writerow(['user_id', 'national_id', 'name', 'email', 'phone', 'password_hash', 'role'])
        writer.writerow([
            user_id,
            national_id,
            name,
            email,
            phone,
            password_hash,
            'CITIZEN'
        ])

    flash(f'Registration successful! You can now login with email: {email}', 'success')
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET'])
def login_page():
    """Login page route."""
    # If already logged in, redirect based on role (don't show login page)
    if 'user_id' in session and session.get('user_id'):
        role = session.get('role', '').upper()
        if role == 'ADMIN':
            return redirect(url_for('admin.admin_dashboard'))
        elif role == 'DELIVERY':
            return redirect(url_for('delivery.delivery_dashboard'))
        elif role == 'CITIZEN':
            return redirect(url_for('citizen.citizen_dashboard'))
        else:
            return redirect(url_for('user_controller.dashboard'))
    
    # Clear any error messages when showing login page (to avoid showing stale errors)
    # Only show errors that are specifically for login failures
    return render_template('Login.html')


@app.before_request
def require_login():
    """Protect routes that require authentication."""
    # Routes that don't require login
    public_routes = ['index', 'register', 'login_page', 'static', 'user_controller.logout']
    
    # Skip authentication for public routes
    if request.endpoint in public_routes:
        return None
    
    # Skip authentication for login POST (handled by user_controller)
    if request.endpoint == 'user_controller.login' and request.method == 'POST':
        return None
    
    # Skip if no endpoint (e.g., favicon requests, 404s)
    if not request.endpoint:
        return None
    
    # Check if user is logged in - verify session has valid user_id
    user_id = session.get('user_id')
    if not user_id or user_id == '':
        # Don't flash error if already on login page to avoid duplicate messages
        if request.endpoint != 'login_page':
            flash('You must log in first', 'error')
        return redirect(url_for('login_page'))
    
    # Protect admin routes
    if request.endpoint and request.endpoint.startswith('admin.'):
        if session.get('role', '').upper() != 'ADMIN':
            flash('Access denied. Admin privileges required.', 'error')
            return redirect(url_for('login_page'))
    
    # Protect delivery routes
    if request.endpoint and request.endpoint.startswith('delivery.'):
        if session.get('role', '').upper() != 'DELIVERY':
            flash('Access denied. Delivery agent privileges required.', 'error')
            return redirect(url_for('login_page'))
    
    # Protect user dashboard
    if request.endpoint == 'user_controller.dashboard':
        # Already checked for login above
        pass
    
    # Protect citizen routes
    if request.endpoint and request.endpoint.startswith('citizen.'):
        if session.get('role', '').upper() != 'CITIZEN':
            flash('Access denied. Citizen privileges required.', 'error')
            return redirect(url_for('login_page'))


if __name__ == '__main__':
    # Initialize all CSV files and ensure admin/delivery users exist
    ensure_admin_delivery_users()
    init_requests_csv()
    init_deliveries_csv()
    
    # Run the app
    app.run(debug=True)
