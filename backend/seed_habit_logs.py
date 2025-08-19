from datetime import datetime, timedelta
from app import app, db
from models import HabitLog  # adjust this import based on your app structure

# habit_id 1 = brush teeth x2 for user ryanRYAN1
HABIT_ID = 1

# Sample data (status: 1 = completed, 0 = missed)
sample_logs = [
    ('2025-08-01', True),
    ('2025-08-02', True),
    ('2025-08-03', False),
    ('2025-08-04', True),
    ('2025-08-05', True),
    ('2025-08-06', True),
    ('2025-08-07', False),
    ('2025-08-08', True),
    ('2025-08-09', True),
    ('2025-08-18', True),
    ('2025-08-17', True),
    ('2025-08-16', True)
]

def seed_logs():
    with app.app_context():
        for date_str, status in sample_logs:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

            # Avoid duplicate entries
            existing = HabitLog.query.filter_by(habit_id=HABIT_ID, date=date_obj).first()
            if not existing:
                log = HabitLog(
                    habit_id=HABIT_ID,
                    date=date_obj,
                    status=status
                )
                db.session.add(log)
                print(f"Added: {date_str} - {'✔' if status else '❌'}")
            else:
                print(f"Skipped (exists): {date_str}")

        db.session.commit()
        print("Seeding complete!")

if __name__ == '__main__':
    seed_logs()
