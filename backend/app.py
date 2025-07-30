from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from datetime import date, timedelta
from models import db, User, Habit, HabitLog
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

import os
import re

app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habits.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

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
    habit = Habit(name=data.get('name'), user_id=current_user.id, category=data.get('category'))
    db.session.add(habit)
    db.session.commit()
    return jsonify({'message': 'Habbit Added'})

@app.route('/api/habits', methods=['GET'])
@login_required
def get_habits():
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    return jsonify([{'id': h.id, 'name': h.name, 'completed': h.completed, 'category': h.category} for h in habits])

# mark habit as completed/done
@app.route('/api/habits/<int:habit_id>/complete', methods=['POST'])
@login_required
def complete_habit(habit_id):
    today = date.today()
    log = HabitLog.query.filter_by(habit_id=habit_id, date=today).first()
    if not log:
        log = HabitLog(habit_id=habit_id, date=today)
    log.completed = True
    db.session.add(log)
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id == current_user.id:
        habit.completed = True
        db.session.commit()
    return jsonify({'message': 'Habit Marked as Complete'})

# change one specific habit from 'done' to 'undone'
@app.route('/api/habits/<int:habit_id>/undo', methods=['POST'])
@login_required
def undo_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id == current_user.id:
        habit.completed = False
        db.session.commit()
    return jsonify({'message': 'Habit marked as undone'})

# reset all habits marked as 'done' to 'undone'
@app.route('/api/habits/reset', methods=['POST'])
@login_required
def reset_habits():
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    for h in habits:
        h.completed = False
    db.session.commit()
    return jsonify({'message': 'Habits Reset'})

# remove a specific habit on list
@app.route('/api/habits/<int:habit_id>', methods=['DELETE'])
@login_required
def delete_habit(habit_id):
    habit = Habit.query.get_or_404(habit_id)
    
    # Make sure the habit belongs to the current user
    if habit.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(habit)
    db.session.commit()
    return jsonify({'message': 'Habit deleted successfully'})

# clear all habits from list
@app.route('/api/habits/clear', methods=['POST'])
@login_required
def clear_habits():
    Habit.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'message': 'All habits cleared'})

# generate log to track daily completeness data
@app.route('/api/habits/<int:habit_id>log', methods=['POST'])
def add_habit_log(habit_id):
    data = request.get_json()
    log_date = date.fromisoformat(data.get('date'))
    status = data.get('status', True)

    log = HabitLog.query.filter_by(habit_id=habit_id, date=log_date).first()
    if log:
        log.status = status #update existing instead of inserting
    else:
        log = HabitLog(habit_id=habit_id, date=log_date, status=status)
        db.session.add(log)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Log already exists for that date'}), 400
    
    return jsonify({'message': 'Log saved'}), 200

# get logs for a habit
@app.route('/api/habits/<int:habit_id>/logs', methods=['GET'])
def get_habit_logs(habit_id):
    logs = HabitLog.query.filter_by(habit_id=habit_id).order_by(HabitLog.date).all()
    return jsonify([{'date': log.date.isoformat(), 'status': log.status}
                    for log in logs])

# ----------------------------------------------------------
#  HABIT STREAKS
def calculate_streak(habit_id):
    logs = (
        HabitLog.query.filter_by(habit_id=habit_id, completed=True).order_by(HabitLog.date.desc()).all()
    )
    streak = 0
    today = date.today()

    for i, log in enumerate(logs):
        expected_date = today - timedelta(days=i)
        if log.date == expected_date:
            streak += 1
        else:
            break
    return streak

@app.route('/api/habits/<int:habit_id>/streak', methods=['GET'])
@login_required
def get_streak(habit_id):
    streak = calculate_streak(habit_id)
    return jsonify({"streak": streak})

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

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged Out'})

# get user info
@app.route('/api/user/', methods=['GET'])
@login_required
def get_user():
    return jsonify({ 'username': current_user.username,
                    'first_name': current_user.first_name,
                    'last_name': current_user.last_name,
                    })

#--------------------------------------------------------
# SERVE FRONTEND AND MAIN

@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
