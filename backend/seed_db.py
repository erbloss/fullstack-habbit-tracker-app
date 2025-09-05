from datetime import date, timedelta
import random
from app import app, db
from models import HabitLog, HabitSnapshots

# Seeds the habits logs for habit IDs 1-5
HABIT_IDS = [1, 2, 3, 4, 5]
USER_ID = 1

# Seed habits for range 30 days ago up to today
end_date = date.today()
start_date = end_date - timedelta(days=30)

def seed_logs():
    with app.app_context():
        for habit_id in HABIT_IDS:
            for i in range(31):  # 0 through 30 days ago
                current_date = start_date + timedelta(days=i)
                status = random.choice([True, False])  # Randomly mark as complete or not

                # Avoid duplicates
                existing = HabitLog.query.filter_by(habit_id=habit_id, date=current_date).first()
                if not existing:
                    log = HabitLog(
                        habit_id=habit_id,
                        date=current_date,
                        status=status
                    )
                    db.session.add(log)
                    print(f"Habit {habit_id} - {current_date} - {'✔' if status else '❌'}")
                else:
                    print(f"Skipped (exists): Habit {habit_id} - {current_date}")

        db.session.commit()
        print("Habit log seeding complete!")

# seed HabitSnapshots with random num of total daily habits within 30 day range
def seed_snapshots():
    with app.app_context():
        for i in range (31):
            current_date = start_date + timedelta(days=i)
            total_habits = random.choice([6, 7, 8, 9, 10]) #random num daily total habits

            existing_snap = HabitSnapshots.query.filter_by(user_id=USER_ID, snapshot_date=current_date).first()
            if not existing_snap:
                snap = HabitSnapshots(
                    user_id=USER_ID,
                    snapshot_date=current_date,
                    total_habits=total_habits,
                    created_at=end_date
                )
                db.session.add(snap)
                print(f"Snapshot created for date: {current_date}")
            else: 
                print(f"Skipped snapshot for {current_date}")
            db.session.commit()
            print("Snapshot seeding complete!")

if __name__ == '__main__':
    seed_logs()
    seed_snapshots()
