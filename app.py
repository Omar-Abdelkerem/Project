from flask import Flask, render_template, request
import csv
import uuid
import os

app = Flask(__name__, template_folder='templates', static_folder='static')

DATA_FILE = os.path.join('data', 'users.csv')


def init_users_csv():
    os.makedirs('data', exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', newline='', encoding='utf-8') as f:
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



@app.route('/')
def index():
    return render_template('index.html')



@app.route('/register', methods=['GET', 'POST'])
def register():
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

    user_id = str(uuid.uuid4())
    password_hash = password 

    init_users_csv()

    with open(DATA_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            user_id,
            national_id,
            name,
            email,
            phone,
            password_hash,
            'CITIZEN'
        ])

    return render_template('success.html')



@app.route('/login')
def login():
    return render_template('login.html')



if __name__ == '__main__':
    init_users_csv()
    app.run(debug=True)
