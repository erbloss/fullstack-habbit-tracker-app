from functools import wraps
from sqlite3 import IntegrityError
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import date
from models import Habit, HabitLog, HabitSnapshots, User
from extensions import db

# THIS FILE DEFINES LOGGING OF HABITS

logs_bp = Blueprint('logs', __name__)

def secure_route(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function



# generate log to track daily completeness data
@logs_bp.route('/api/habits/<int:habit_id>/log', methods=['POST'])
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
    with logs_bp.app_context():
        today = date.today()
        habits = Habit.query.all()

        for habit in habits:
            existing_log = HabitLog.query.filter_by(habit_id=habit.id, date=today).first()
            if not existing_log: #no log exists
                log = HabitLog(habit_id=habit.id, date=today, status=False)
                db.session.add(log)
        db.session.commit()


# get logs for one particular habit
@logs_bp.route('/api/habits/<int:habit_id>/getlogs', methods=['GET'])
@secure_route
def get_habit_logs(habit_id):
    logs = HabitLog.query.filter_by(habit_id=habit_id).order_by(HabitLog.date).all()
    return jsonify([{'date': log.date.isoformat(), 
                     'status': log.status}
                    for log in logs])

# get logs for all habits
@logs_bp.route('/api/habits/getlogs', methods=['GET'])
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
    with logs_bp.app_context():
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
@logs_bp.route('/api/habit_snapshots/<int:user_id>')
def get_habit_snapshots(user_id):
    snapshots = HabitSnapshots.query.filter_by(user_id=user_id).order_by(HabitSnapshots.snapshot_date.desc()).all()
    return jsonify([{
            "snapshot_date": s.snapshot_data.isoformat(),
            "total_habits": s.total_habits
        } for s in snapshots 
    ])

# computes the completion rate of 
@logs_bp.route('/api/completion_history/<int:user_id>')
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
