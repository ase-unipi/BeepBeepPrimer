from celery import Celery
from stravalib import client as c # Need to expose the ApiV3 import from stravalib.client (don't ask...)
from monolith.database import db, User, Run
from celery.schedules import crontab
from monolith.mail_service import _send_reports

import datetime

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)
celery.conf.timezone = 'Europe/Rome'

celery.conf.beat_schedule = {
    'send_reports-every-midnight': {
        'task': 'monolith.background.send_reports',
        'schedule': crontab(hour = 0, minute = 0)
    }
}

_APP = None


def create_context():
    global _APP
    # lazy init
    print(_APP) #for testing shows what kind of app we use
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
        _APP = app
    else:
        app = _APP
    return app


@celery.task
def fetch_runs_for_user(id_):
    app = create_context()
    with app.app_context():
        q = db.session.query(User).filter(User.id == id_)
        user = q.first()
        return fetch_runs(user)


def activity2run(user, activity):
    """Used by fetch_runs to convert a strava run into a DB entry.
    """
    run = Run()
    run.runner = user
    run.strava_id = activity.id
    run.name = activity.name
    run.distance = activity.distance
    run.elapsed_time = activity.elapsed_time.total_seconds()
    run.average_speed = activity.average_speed
    run.average_heartrate = activity.average_heartrate
    run.total_elevation_gain = activity.total_elevation_gain
    run.start_date = activity.start_date
    return run


def fetch_runs(user):
    client = c.Client(access_token=user.strava_token)
    print(client.protocol)
    runs = 0

    for activity in client.get_activities():
        print(activity)
        if activity.type != 'Run':
            continue
        q = db.session.query(Run).filter(Run.strava_id == activity.id)
        run = q.first()
        if run is None:
            db.session.add(activity2run(user, activity))
            runs += 1

    db.session.commit()
    return runs

# @celery.task()
# def send_repo():
#     print("ciao a tutti")

# @celery.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(10.0, send_repo)
@celery.task()
def send_reports():
    app = create_context()
    with app.app_context():
        _send_reports()

# @celery.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):

#     # Execute every 10 seconds
#     sender.add_periodic_task(10.0, send_reports)
    
#     # # Executes every day at 00:00 a.m.
#     # sender.add_periodic_task(
#     #     crontab(hour=0, minute=0),
#     #     send_reports()
#     # )

