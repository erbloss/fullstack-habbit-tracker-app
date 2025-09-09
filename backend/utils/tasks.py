from datetime import date
from extensions import db
from models import User, Habit, HabitLog, HabitSnapshots

# Fill in any missing HabitLog entries (default status = False)
def create_missing_logs(app):
    with app.app_context():
        today = date.today()
        habits = Habit.query.all()

        for habit in habits:
            existing_log = HabitLog.query.filter_by(habit_id=habit.id, date=today).first()
            if not existing_log:
                log = HabitLog(habit_id=habit.id, date=today, status=False)
                db.session.add(log)

        db.session.commit()
        print(f"[✓] Missing logs created for {today}")

# Log the total number of habits marked complete for each user (snapshot)
def log_daily_habit_snapshot(app):
    with app.app_context():
        today = date.today()
        users = User.query.all()

        for user in users:
            total_habits = Habit.query.filter_by(user_id=user.id, status=True).count()

            # Avoid duplicate snapshots
            existing_snapshot = HabitSnapshots.query.filter_by(user_id=user.id, snapshot_date=today).first()
            if not existing_snapshot:
                snapshot = HabitSnapshots(
                    user_id=user.id,
                    snapshot_date=today,
                    total_habits=total_habits
                )
                db.session.add(snapshot)

        db.session.commit()
        print(f"[✓] Habit snapshots logged for {today}")

# Reset all habit statuses to False (undone)
def reset_habits(app):
    with app.app_context():
        habits = Habit.query.all()

        for habit in habits:
            habit.status = False

        db.session.commit()
        print(f"[✓] All habits reset for a new day ({date.today()})")
