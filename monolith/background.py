from celery import Celery
#IMPORT SETTING FOR FETCH
from stravalib import Client
# IMPORT SETTING FOR MAIL
from datetime import time, datetime, timedelta
from flask_mail import Mail, Message

#IMPORT SETTING FOR BOTH FETCH AND MAIL
from monolith.database import db, User, Run, Report

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None


@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0, fetch_all_runs)

    sender.add_periodic_task(30.0, send_all_mail)


@celery.task
def fetch_all_runs():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP

    runs_fetched = {}

    with app.app_context():
        q = db.session.query(User)
        for user in q:
            if user.strava_token is None:
                continue
            print('Fetching Strava for %s' % user.email)
            runs_fetched[user.id] = fetch_runs(user)

    return runs_fetched


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
    client = Client(access_token=user.strava_token)
    runs = 0

    for activity in client.get_activities(limit=10):
        if activity.type != 'Run':
            continue
        q = db.session.query(Run).filter(Run.strava_id == activity.id)
        run = q.first()

        if run is None:
            db.session.add(activity2run(user, activity))
            runs += 1

    db.session.commit()
    return runs

#CELERY TASK FOR MAIL
@celery.task
def send_all_mail():
    print('sending')
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP
    mail = Mail(app)
    mail.init_app(app=app)
    with app.app_context():
        users = db.session.query(User).filter()
        for user in users:
            mail = db.session.query(Mail).filter(Mail.id == user.id)
            if time.time() - mail.timestamp >= mail.choice_time:        #check of the choice of the user
                body = prepare_body(user,choice_time)
                if body:
                    msg = Message('Your BeepBeep Report', sender=app.config['MAIL_USERNAME'], recipients=[user.email])
                    msg.body = body
                    mail.send(msg)


def prepare_body(user,choice_time):
    body = ""
    with app.app_context():
        runs = db.session.query(Run).filter(Run.runner == user, Run.start_date >= (datetime.now() - timedelta(hour=choice_time)))
    if runs.count() == 0:
        return None
    for run in runs:
        body += "name: " + run.name + "\n" + "distance: " + str(run.distance) + "\n" + "start_date: " + str(run.start_date) + "\n" + "average_speed: " + str(run.average_speed) + "\n"
        body += "elapsed_time: " + str(run.elapsed_time) + "\n" + "average_heartrate: " + str(run.average_heartrate) + "\n" + "total_elevation_gain: " + str(run.total_elevation_gain)+ "\n\n\n"
    return body
