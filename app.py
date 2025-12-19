from flask import Flask, render_template, request, redirect, url_for, flash, session
import csv
import uuid
import os
import sys

# Add project root to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from controllers.UserController import user_controller
from controllers.admin_controller import admin_bp
from controllers.application_controller import application_bp

# Create Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get("FLASK_SECRET", "dev-secret-change-me-12345")

# Register Blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(user_controller)
app.register_blueprint(application_bp)

# Data files paths
DATA_FOLDER = os.path.join(BASE_DIR, 'data')
USERS_FILE = os.path.join(DATA_FOLDER, 'users.csv')
REQUESTS_FILE = os.path.join(DATA_FOLDER, 'requests.csv')


def init_csv_files():
    """Initialize CSV files with headers if they don't exist"""
    os.makedirs(DATA_FOLDER, exist_ok=True)
    
    # Initialize users.csv
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['user_id', 'national_id', 'name', 'email', 
                           'phone', 'password_hash', 'role'])
            # Add default admin user
            writer.writerow(['admin-001', '12345678901234', 'Admin User', 
                           'admin@gmail.com', '01234567890', '1234', 'admin'])
            # Add default citizen user
            writer.writerow(['user-001', '98765432109876', 'Test User', 
                           'user@gmail.com', '01098765432', '0000', 'citizen'])
    
    # Initialize requests.csv
    if not os.path.exists(REQUESTS_FILE):
        with open(REQUESTS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['request_id', 'user_id', 'user_name', 'type', 
                           'description', 'status', 'created_at'])


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'GET':
        return render_template('register.html', errors=[])
    
    # Get form data
    name = request.form.get('name', '').strip()
    national_id = request.form.get('national_id', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    password = request.form.get('password', '')
    confirm = request.form.get('confirm_password', '')
    
    # Validation
    errors = []
    if not name:
        errors.append('Name is required')
    if len(national_id) != 14 or not national_id.isdigit():
        errors.append('National ID must be exactly 14 digits')
    if not email or '@' not in email:
        errors.append('Valid email is required')
    if not phone or len(phone) < 11:
        errors.append('Valid phone number is required')
    if not password or len(password) < 4:
        errors.append('Password must be at least 4 characters')
    if password != confirm:
        errors.append('Passwords do not match')
    
    # Check if email already exists
    if not errors:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['email'] == email:
                    errors.append('Email already registered')
                    break
    
    if errors:
        return render_template('register.html', errors=errors, 
                             name=name, national_id=national_id, 
                             email=email, phone=phone)
    
    # Generate user ID and save
    user_id = str(uuid.uuid4())[:8]
    with open(USERS_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([user_id, national_id, name, email, phone, password, 'citizen'])
    
    flash('Registration successful! Please login.', 'success')
    return redirect(url_for('login_page'))


@app.route('/login', methods=['GET'])
def login_page():
    """Login page"""
    return render_template('Login.html')


@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_csv_files()
    print("=" * 50)
    print("Flask Application Starting...")
    print(f"Data folder: {DATA_FOLDER}")
    print(f"Users file: {USERS_FILE}")
    print(f"Requests file: {REQUESTS_FILE}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)