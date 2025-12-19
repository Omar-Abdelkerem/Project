from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import csv
import os
from models.UserModel import users


user_controller = Blueprint('user_controller', __name__)


@user_controller.route('/login', methods=['POST'])
def login():
    """Handle user login"""
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    if not email or not password:
        flash('Please enter both email and password', 'error')
        return redirect(url_for('login_page'))
    
    # Read users from CSV
    try:
        USERS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'users.csv')
        
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['email'] == email and row['password_hash'] == password:
                    # Login successful - store in session
                    session['user_id'] = row['user_id']
                    session['user_name'] = row['name']
                    session['user_email'] = row['email']
                    session['user_role'] = row['role']
                    
                    flash(f'Welcome back, {row["name"]}!', 'success')
                    
                    # Redirect based on role
                    if row['role'] == 'admin':
                        return redirect(url_for('admin.admin_dashboard'))
                    else:
                        return redirect(url_for('application.citizen_dashboard'))
        
        # If we reach here, login failed
        flash('Invalid email or password', 'error')
        return redirect(url_for('login_page'))
    
    except FileNotFoundError:
        flash('System error: Users database not found', 'error')
        return redirect(url_for('login_page'))


@user_controller.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')