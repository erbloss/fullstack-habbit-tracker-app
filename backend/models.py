from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import date

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    habits = db.relationship('Habit', backref='user', lazy=True)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    logs= db.relationship('HabitLog', backref='habit', lazy=True)

# ensure only one record per habit per date
class HabitLog(db.Model):
    __tablename__ = 'habit_log'
    __table_args__ = (
        db.UniqueConstraint('habit_id', 'date', name='unique_habit_date'),
    )
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Boolean, default=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
