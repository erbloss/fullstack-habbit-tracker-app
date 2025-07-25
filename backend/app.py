from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from models import db, User, Habit

from werkzeug.security import generate_password_hash, check_password_hash

import os

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habits.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
CORS(app, supports_credentials=True)

#--------------------------------------------------------------
# LOGIN SETUP
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

#--------------------------------------------------------------
# MANIPULATING HABITS
@app.route('/api/habits', methods=['POST'])
@login_required
def add_habit():
    data = request.get_json()
    habit = Habit(name=data.get('name'), user_id=current_user.id)
    db.session.add(habit)
    db.session.commit()
    return jsonify({'message': 'Habbit Added'})

@app.route('/api/habits/<int:habit_id>/complete', methods=['POST'])
@login_required
def complete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id == current_user.id:
        habit.completed = True
        db.session.commit()
    return jsonify({'message': 'Habit Marked as Complete'})

@app.route('/api/habits', methods=['GET'])
@login_required
def get_habits():
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    return jsonify([{'id': h.id, 'name': h.name, 'completed': h.completed} for h in habits])

@app.route('/api/habits/reset', methods=['POST'])
@login_required
def reset_habits():
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    for h in habits:
        h.completed = False
    db.session.commit()
    return jsonify({'message': 'Habits Reset'})

# ----------------------------------------------------------
# LOGGING IN AND OUT
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data.get('username')).first()
    if user and check_password_hash(user.password, data.get('password')):
        login_user(user)
        return jsonify({'message': 'Logged In'})
    return jsonify({'error': 'Error Logging In.  Invalid Credentials'}), 401

# allows user to create account.  Password is hashed for security
# add complexity to username and password requirements
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = generate_password_hash(data.get('password'))
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'User already exists'}), 409
    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Registered Successfully'})

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged Out'})

#--------------------------------------------------------
# SERVE FRONTEND AND MAIN
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
