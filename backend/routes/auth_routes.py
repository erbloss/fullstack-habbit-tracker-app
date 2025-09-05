import re
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import  User
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

# THIS FILE DEFINES LOGGING IN, LOGGING OUT, REGISTERING

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()

    if user and check_password_hash(user.password, data.get('password')):
        login_user(user, remember=False)
        return jsonify({'message': 'Logged In'})
    return jsonify({'error': 'Error Logging In.  Invalid Credentials'}), 401

# allows user to create account.  Password is hashed for security
# add complexity to username and password requirements
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("Received registration data:", data)  # <--- TESTING

    username = data.get('username')
    password_plain = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if not username or not password_plain or not first_name or not last_name:
        return jsonify({'error': 'Missing required fields'}), 400
    if len(username) < 6 or not re.match("^[a-zA-Z0-9]+$", username):
        return jsonify({'error': 'Username must be at least 6 characters and alphanumeric only.'}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 409
    
    password = generate_password_hash(password_plain)
    user = User(username=username, password=password, first_name=first_name, last_name=last_name)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registered Successfully'})

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged Out'})

# get user info
@auth_bp.route('/user/', methods=['GET'])
@login_required
def get_user():
    return jsonify({ 'username': current_user.username,
                    'first_name': current_user.first_name,
                    'last_name': current_user.last_name,
                    'id': current_user.id
                    })