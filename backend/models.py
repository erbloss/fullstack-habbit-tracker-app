from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date, datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    habits = db.relationship('Habit', backref='user', lazy=True)

class Habit(db.Model):
    __tablename__ = 'habits'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_created = db.Column(db.Date, nullable=False)
    date_deleted = db.Column(db.Date, nullable=True)

    logs= db.relationship('HabitLog', backref='habit', cascade='all, delete-orphan', passive_deletes=True)

# ensure only one record per habit per date
class HabitLog(db.Model):
    __tablename__ = 'habit_log'
    __table_args__ = (
        db.UniqueConstraint('habit_id', 'date', name='unique_habit_date'),
    )
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, default=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habits.id', ondelete='CASCADE'), nullable=False)

class HabitSnapshots(db.Model):
    __tablename__ = 'habit_snapshots'
    user_id = db.Column(db.String(100), nullable=False, primary_key=True)
    snapshot_date = db.Column(db.Date, primary_key=True)
    total_habits = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

