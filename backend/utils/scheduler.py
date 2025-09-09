from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from .tasks import create_missing_logs, log_daily_habit_snapshot, reset_habits

# import and schedule functions from tasks.py
def init_scheduler(app):
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=lambda: create_missing_logs(app), trigger=CronTrigger(hour=23, minute=59))
    scheduler.add_job(func=lambda: log_daily_habit_snapshot(app), trigger=CronTrigger(hour=23, minute=59))
    scheduler.add_job(func=lambda: reset_habits(app), trigger=CronTrigger(hour=23, minute=59))
    scheduler.start()
