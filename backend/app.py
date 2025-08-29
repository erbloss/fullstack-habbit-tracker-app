from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import date, timedelta
from models import db, User, Habit, HabitLog, HabitSnapshots
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import re

def secure_route(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function


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

login_manager.unauthorized_handler
def unauthorized():
    return jsonify({'error': 'unauthorized'}), 401

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables():
    db.create_all()

#--------------------------------------------------------------
# MANIPULATING HABITS

# add a new habit
@app.route('/api/habits', methods=['POST'])
@login_required
def add_habit():
    data = request.get_json()
    habit = Habit(name=data.get('name'), user_id=current_user.id, category = data.get('category'), date_created = date.today())
    db.session.add(habit)
    db.session.commit()
    return jsonify({'message': 'Habbit Added'})

# get all habits for the logged in user
@app.route('/api/habits', methods=['GET'])
@login_required
def get_habits():
    today = date.today()
    habits = Habit.query.filter_by(user_id=current_user.id).all()

    # create a daily log instance for all habits if none exists
    for habit in habits:
        existing_log= HabitLog.query.filter_by(habit_id=habit.id, date=today).first()
        if not existing_log:
            log = HabitLog(habit_id=habit.id, date=today, status=False)
            db.session.add(log)
    db.session.commit() 

    return jsonify([{
        'id': h.id, 
        'name': h.name, 
        'status': h.status,
        'category': h.category, 
        'date_created': h.date_created} for h in habits])

# mark habit status as completed/done
@app.route('/api/habits/<int:habit_id>/markDone', methods=['POST'])
@login_required
def complete_habit(habit_id):
    today = date.today()

    # Update HabitLog
    log = HabitLog.query.filter_by(habit_id=habit_id, date=today).first()
    if not log:
        log = HabitLog(habit_id=habit_id, date=today)
    # set Log status to true
    log.status = True
    db.session.add(log)
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id == current_user.id:
        # Set main habit status to true
        habit.status = True
        db.session.commit()
    return jsonify({'message': 'Habit Marked as Complete'})

# change one specific habit from 'done' to 'undone'
@app.route('/api/habits/<int:habit_id>/markUndone', methods=['POST'])
@login_required
def undo_habit(habit_id):
    today = date.today()
    
    # Update HabitLog
    log = HabitLog.query.filter_by(habit_id=habit_id, date=today).first()
    if log:
        log.status = False
    else:
        # If no log exists for today, create one with False
        log = HabitLog(habit_id=habit_id, date=today, status=False)
        db.session.add(log)

    # Update Habit
    habit = Habit.query.get_or_404(habit_id)
    if habit.user_id == current_user.id:
        habit.status = False
        db.session.commit()

    return jsonify({'message': 'Habit marked as undone'})


# reset all habits marked as 'done' to 'undone'
@app.route('/api/habits/reset', methods=['POST'])
@login_required
def reset_habits():
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    for h in habits:
        h.status = False
    db.session.commit()
    return jsonify({'message': 'Habits Reset'})

# remove a specific habit on list
@app.route('/api/habits/<int:habit_id>', methods=['DELETE'])
@login_required
def delete_habit(habit_id):
    try:
        habit = Habit.query.get_or_404(habit_id)

        if habit is None:
            return jsonify({'error': 'Habit not found'}), 404

        if habit.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403

        db.session.delete(habit)
        db.session.commit()
        return jsonify({'message': 'Habit deleted successfully'})

    except Exception as e:
        import traceback
        print("ERROR DELETING HABIT:")
        traceback.print_exc() 
        return jsonify({'error': 'Internal Server Error'}), 500


# clear all habits from list
@app.route('/api/habits/clear', methods=['POST'])
@login_required
def clear_habits():
    Habit.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'message': 'All habits cleared'})

#------------------------------------------------------------------
#    HABIT LOGGING

# generate log to track daily completeness data
@app.route('/api/habits/<int:habit_id>/log', methods=['POST'])
@secure_route
def add_habit_log(habit_id):
    data = request.get_json()
    log_date = date.fromisoformat(data.get('date'))
    status = data.get('status', True)

    log = HabitLog.query.filter_by(habit_id=habit_id, date=log_date).first()
    if log:
        #update existing instead of inserting
        log.status = status 
    else:
        # create a new log
        log = HabitLog(habit_id=habit_id, date=log_date, status=status)
        db.session.add(log)
    
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Log already exists for that date'}), 400
    
    return jsonify({'message': 'Log saved'}), 200

# create log entry for any missing logs for a complete data set
def create_missing_logs():
    with app.app_context():
        today = date.today()
        habits = Habit.query.all()

        for habit in habits:
            existing_log = HabitLog.query.filter_by(habit_id=habit.id, date=today).first()
            if not existing_log: #no log exists
                log = HabitLog(habit_id=habit.id, date=today, status=False)
                db.session.add(log)
        db.session.commit()


# get logs for one particular habit
@app.route('/api/habits/<int:habit_id>/getlogs', methods=['GET'])
@secure_route
def get_habit_logs(habit_id):
    logs = HabitLog.query.filter_by(habit_id=habit_id).order_by(HabitLog.date).all()
    return jsonify([{'date': log.date.isoformat(), 
                     'status': log.status}
                    for log in logs])

# get logs for all habits
@app.route('/api/habits/getlogs', methods=['GET'])
@secure_route
def get_all_habit_logs():
    user_habits = Habit.query.filter_by(user_id=current_user.id).all()
    habit_ids = [habit.id for habit in user_habits]
    logs = HabitLog.query.filter(HabitLog.habit_id.in_(habit_ids)).order_by(HabitLog.date.asc()).all()
    logs_data = [
        {'habit_id': log.habit_id,
         'date': log.date.isoformat(),
         'status': log.status}
         for log in logs
    ]
    return jsonify(logs_data)
   
# log snapshot for daily number of tasks for each user
def log_daily_habit_snapshot():
    with app.app_context():
        today = date.today()
        users = User.query.all()
        for user in users:
            total_habits = Habit.query.filter_by(user_id=user.id, status=True).filter(Habit.date_deleted.is_(None)).count()

            # check to ensure no duplicates
            existing = HabitSnapshots.query.filter_by(user_id=user.id, snapshot_date=today).first()
            if not existing:
                snapshot = HabitSnapshots(
                    user_id=user.id,
                    snapshot_date=today,
                    total_habits=total_habits
                )
                db.session.add(snapshot)
        db.session.commit()
        print(f"Habit snapshots logged for {today}")
    
 # method to get the habit snapshots for users 
@app.route('/api/habit_snapshots/<int:user_id>')
def get_habit_snapshots(user_id):
    snapshots = HabitSnapshots.query.filter_by(user_id=user_id).order_by(HabitSnapshots.snapshot_date.desc()).all()
    return jsonify([{
            "snapshot_date": s.snapshot_data.isoformat(),
            "total_habits": s.total_habits
        } for s in snapshots 
    ])

# computes the completion rate of 
@app.route('/api/completion_history/<int:user_id>')
@login_required
def get_completion_history(user_id):
    today = date.today()

    snapshots = HabitSnapshots.query.filter_by(user_id=user_id).order_by(HabitSnapshots.snapshot_date.desc()).all()
    results = []

    for snapshot in snapshots:
        snapshot_date = snapshot.snapshot_date
        total_habits = snapshot.total_habits

        # get all logs for that user/date
        habits = Habit.query.filter_by(user_id=user_id).all()
        habit_ids = [h.id for h in habits]

        logs = HabitLog.query.filter(
            HabitLog.habit_id.in_(habit_ids),
            HabitLog.date == snapshot_date,
            HabitLog.status == True
        ).count()

        completion = (logs / total_habits) * 100 if total_habits else 0

        results.append({
            'date': snapshot_date.isoformat(),
            'completion': round(completion, 2)
        })

    return jsonify(results)



# ----------------------------------------------------------
#  HABIT STREAKS AND COMPLETION

def calculate_streak(habit_id):
    logs = HabitLog.query.filter_by(habit_id=habit_id, status=True).all()
    completed_dates = {log.date.date() if hasattr(log.date, 'date') else log.date for log in logs}
    streak = 0
    today = date.today() - timedelta(days=1)

    while (today - timedelta(days=streak)) in completed_dates:
        streak += 1
    return streak

@app.route('/api/habits/<int:habit_id>/streak', methods=['GET'])
@secure_route
def get_streak(habit_id):
    streak = calculate_streak(habit_id)
    return jsonify({"streak": streak})

# get the completion rate for a habit in the last 30 days
@app.route('/api/habits/<int:habit_id>/rate', methods=['GET'])
@secure_route
def get_completion_rate(habit_id):
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    logs = HabitLog.query.filter(
        HabitLog.habit_id == habit_id,
        HabitLog.date >= thirty_days_ago
    ).all()

    total = 30
    completed = sum(1 for log in logs if log.status)
    rate = (completed / total) * 100

    return jsonify({
        "habit_id": habit_id,
        "completion_rate": round(rate, 2),
        "completed_days": completed,
        "total_days": total
    })


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

# set up scheduler to execute functions at 11:59pm -->
# fills missing logs,
# logs daily habit snapshot, 
# and resets all habits to undone
scheduler = BackgroundScheduler()
scheduler.add_job(create_missing_logs, CronTrigger(hour=23, minute=59))
scheduler.add_job(log_daily_habit_snapshot, CronTrigger(hour=23, minute=59))
scheduler.add_job(reset_habits, CronTrigger(hour=23, minute=59))
scheduler.start()


if __name__ == '__main__':
    app.run(debug=True)
