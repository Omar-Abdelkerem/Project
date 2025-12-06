from flask import Blueprint, render_template, request, redirect, url_for
from models.UserModel import users

user_controller = Blueprint('user_controller', _name_)


@user_controller.route('/')
def login_page():
    return render_template('Login.html')


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
    return '''
        <h1>Welcome to Fast ID System</h1>
        <p>Request National ID Card</p>
        <p>Request Bank Card</p>
        <p>Track Requests</p>
    '''