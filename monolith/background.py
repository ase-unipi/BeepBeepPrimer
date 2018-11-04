from celery import Celery
from stravalib import Client
from monolith.database import db, User, Run

"""
    To have the periodic task running runs celery with
    
    celery -A monolith.background worker -B

"""

BACKEND = BROKER = 'redis://localhost:6379'
celery = Celery(__name__, backend=BACKEND, broker=BROKER)

_APP = None


@celery.on_after_configure.connect
def set_up_tasks(sender, **kwargs):
    sender.add_periodic_task(3600.00, fetch_all_runs, name='fetch_all_the_runs every hour')
    # sender.add_periodic_task(10.00, fetch_all_runs.s(), name='fetch_all_the_runs every hour')
    # use this to test the function


def create_context():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
        _APP = app
    else:
        app = _APP
    return app


@celery.task
def fetch_all_runs():

    app = create_context()
    runs_fetched = {}

    with app.app_context():
        q = db.session.query(User)
        for user in q:
            if user.strava_token is None:
                continue
            print('Fetching Strava for %s' % user.email)
            runs_fetched[user.id] = fetch_runs(user.id)


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


@celery.task
def fetch_runs(id):
    app = create_context()
    with app.app_context():
        q = db.session.query(User).filter(User.id == id)
        user = q.first()
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
