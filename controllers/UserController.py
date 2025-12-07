from flask import Blueprint, render_template, request, redirect, url_for
from models.UserModel import users

user_controller = Blueprint('user_controller', __name__)


@user_controller.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')

    for user in users:
        if user['email'] == email and user['password'] == password:
            return redirect(url_for('user_controller.dashboard'))

    return "Login Failed"


@user_controller.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')