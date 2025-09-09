from functools import wraps
from flask import Blueprint, jsonify
from datetime import date, timedelta
from flask_login import login_required
from models import HabitLog


# THIS FILE DEFINES METHODS AND ROUTES USED BY THE FRONTEND
# RELATED TO HABIT STREAKS AND COMPLETION RATES FOR CHARTS

frontend_bp = Blueprint('frontend', __name__, url_prefix='/api/habits')

def secure_route(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function

def calculate_streak(habit_id):
    logs = HabitLog.query.filter_by(habit_id=habit_id, status=True).all()
    completed_dates = {log.date.date() if hasattr(log.date, 'date') else log.date for log in logs}
    streak = 0
    today = date.today() - timedelta(days=1)

    while (today - timedelta(days=streak)) in completed_dates:
        streak += 1
    return streak

@frontend_bp.route('/<int:habit_id>/streak', methods=['GET'])
@secure_route
def get_streak(habit_id):
    streak = calculate_streak(habit_id)
    return jsonify({"streak": streak})

# get the completion rate for a habit pertaining to the last 30 days
@frontend_bp.route('/<int:habit_id>/rate', methods=['GET'])
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