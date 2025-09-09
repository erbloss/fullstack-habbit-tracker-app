from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import date
from models import Habit, HabitLog
from extensions import db

# THIS FILE DEFINES MANIPULATING HABITS
# i.e., adding them, removing them, etc.

habit_bp = Blueprint('habit', __name__, url_prefix='/api/habits')

@habit_bp.route('', methods=['POST'])
@login_required
def add_habit():
    data = request.get_json()
    habit = Habit(name=data['name'], user_id=current_user.id,
                  category=data['category'], date_created=date.today(), status = 0)
    db.session.add(habit)
    db.session.commit()
    return jsonify({'message': 'Habit added'})

# get all habits for the logged in user
@habit_bp.route('', methods=['GET'])
@login_required
def get_habits():
    today = date.today()
    habits = Habit.query.filter_by(user_id=current_user.id).all()

    # create a daily log instance for all habits if none exists
    for habit in habits:
        existing_log= HabitLog.query.filter_by(habit_id=habit.id, date=today).first()
        if not existing_log:
            log = HabitLog(habit_id=habit.id, date=today)
            db.session.add(log)
    db.session.commit() 

    return jsonify([{
        'id': h.id, 
        'name': h.name, 
        'status': h.status,
        'category': h.category, 
        'date_created': h.date_created} for h in habits])

# mark habit status as completed/done
@habit_bp.route('/<int:habit_id>/markDone', methods=['POST'])
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
@habit_bp.route('/<int:habit_id>/markUndone', methods=['POST'])
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
@habit_bp.route('/reset', methods=['POST'])
@login_required
def reset_habits():
    today = date.today()

    # reset HabitLog status
    logs = HabitLog.query.join(Habit).filter(Habit.user_id == current_user.id, HabitLog.date == today).all()
    for log in logs:
        log.status = False

    # reset Habit Status
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    for h in habits:
        h.status = False

    db.session.commit()
    return jsonify({'message': 'Habits Reset'})

# remove a specific habit on list
@habit_bp.route('/<int:habit_id>', methods=['DELETE'])
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
@habit_bp.route('/clear', methods=['POST'])
@login_required
def clear_habits():
    Habit.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'message': 'All habits cleared'})
