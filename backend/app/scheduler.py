"""
Background jobs (new game mail, statistics) run in-process via APScheduler.

The scheduler must only be started once per deployment, so it is started
from the gunicorn ``post_worker_init`` hook (see ``gunicorn.conf.py``, only
one worker) and from the local development server in ``teleschocken.py`` -
not on import, otherwise ``flask db upgrade`` and the tests would start it too.
"""
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

from app import app

scheduler = BackgroundScheduler(timezone='Europe/Berlin')


def _with_app_context(func):
    def job():
        with app.app_context():
            func()
    return job


def start_scheduler():
    if scheduler.running:
        return
    from app.api.email import send_new_game_mail
    from app.api.statistic import create_statistics

    # coalesce + max_instances=1: a delayed job runs only once and never in parallel
    scheduler.add_job(_with_app_context(send_new_game_mail), 'interval', minutes=1,
                      id='send_new_game_mail', coalesce=True, max_instances=1,
                      replace_existing=True)
    # also run right after start, otherwise every restart would postpone it by 24 hours
    scheduler.add_job(_with_app_context(create_statistics), 'interval', hours=24,
                      id='create_statistics', coalesce=True, max_instances=1,
                      replace_existing=True, next_run_time=datetime.now())
    scheduler.start()
