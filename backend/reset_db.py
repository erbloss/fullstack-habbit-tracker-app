from flask import Flask
from extensions import db
from models import Habit, HabitLog, HabitSnapshots
from app import create_app

app = create_app()

with app.app_context():
    # Drop all tables for habits but keep user data
    Habit.query.delete()
    HabitLog.query.delete()
    HabitSnapshots.query.delete()

    db.session.commit()
    print("Database cleared and tables recreated!")