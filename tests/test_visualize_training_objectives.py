from unittest import mock
from monolith.database import User, Run, Training_Objective
from tests.conftest import mocked_result
from datetime import date, timedelta


def make_and_login_user(client):
    client.post('/create_user', data=dict(submit='Publish', email='mail', firstname='peppe', lastname='p',
                                          password='p', age='1',
                                          weight='1', max_hr='1', rest_hr='1', vo2max='1'))
    client.post('/login', data=dict(submit='Publish', email='mail', password='p'), follow_redirects=True)


def add_training_objective(db, start, finish, km, user=None):
    if user is None:
        user = db.session.query(User).first()
    t = Training_Objective(start_date=start, end_date=finish, kilometers_to_run=km, runner_id=user.id)
    db.session.add(t)
    db.session.commit()


id_run = 1


def add_run(db, start, time, km, user=None):
    global id_run
    if user is None:
        user = db.session.query(User).first()
    r = Run(name="run", strava_id=id_run, distance=km, start_date=start, elapsed_time=time,
            average_speed=10, average_heartrate=0, total_elevation_gain=0, runner_id=user.id)
    id_run += 1
    db.session.add(r)
    db.session.commit()


def test_no_runs_started(client, background_app, celery_session_worker, db_instance):
    make_and_login_user(client)
    add_training_objective(db_instance, date.today(), date.today() + timedelta(1), 5)
    rv = client.get('/training_objectives')
    assert str(date.today()) in rv.data.decode('ascii')
    assert str(date.today() + timedelta(1)) in rv.data.decode('ascii')
    print(rv.data.decode('ascii'))
    assert b'You can do it! Just 5.0 km!' in rv.data


def test_no_runs_failed(client, background_app, celery_session_worker, db_instance):
    make_and_login_user(client)
    add_training_objective(db_instance,date.today() - timedelta(2),date.today() - timedelta(1), 5)
    rv = client.get('/training_objectives')
    assert str(date.today() - timedelta(2)) in rv.data.decode('ascii')
    assert str(date.today() - timedelta(1)) in rv.data.decode('ascii')
    assert b'You missed your goal by 5.0 km...' in rv.data


def test_training_with_run(client, background_app, celery_session_worker, db_instance):
    make_and_login_user(client)
    add_training_objective(db_instance, date.today(), date.today() + timedelta(1), 5)
    add_run(db_instance, date.today(), 60 * 1000, 2000)
    rv = client.get('/training_objectives')
    assert str(date.today()) in rv.data.decode('ascii')
    assert str(date.today() + timedelta(1)) in rv.data.decode('ascii')
    assert b'You can do it! Just 3.0 km!' in rv.data
    add_training_objective(db_instance, date.today(), date.today(), 5)
    rv = client.get('/training_objectives')
    assert str(date.today()) in rv.data.decode('ascii')
    assert str(date.today() + timedelta(1)) in rv.data.decode('ascii')
    assert b'You can do it! Just 3.0 km!' in rv.data


def test_training_failed_with_run(client, background_app, celery_session_worker, db_instance):
    make_and_login_user(client)
    add_training_objective(db_instance, date.today() - timedelta(2), date.today() - timedelta(1), 5)
    add_run(db_instance, date.today() - timedelta(2), 60 * 1000, 4999.1)
    rv = client.get('/training_objectives')
    assert str(date.today() - timedelta(2)) in rv.data.decode('ascii')
    assert str(date.today() - timedelta(1)) in rv.data.decode('ascii')
    assert b'You missed your goal by 0.001 km...' in rv.data


def test_training_success(client, background_app, celery_session_worker, db_instance):
    make_and_login_user(client)
    add_training_objective(db_instance, date.today() - timedelta(2), date.today() - timedelta(1), 5)
    add_run(db_instance, date.today() - timedelta(2), 60 * 1000, 5000)
    rv = client.get('/training_objectives')
    assert str(date.today() - timedelta(2)) in rv.data.decode('ascii')
    assert str(date.today() - timedelta(1)) in rv.data.decode('ascii')
    assert b'Wow! You are done!' in rv.data


def test_training_success_last_date(client, background_app, celery_session_worker, db_instance):
    make_and_login_user(client)
    add_training_objective(db_instance, date.today() - timedelta(2), date.today() - timedelta(1), 5)
    add_run(db_instance,date.today() - timedelta(1),60 * 1000, 5000)
    rv = client.get('/training_objectives')
    assert str(date.today() - timedelta(2)) in rv.data.decode('ascii')
    assert str(date.today() - timedelta(1)) in rv.data.decode('ascii')
    assert b'Wow! You are done!' in rv.data


def test_training_multiple_run(client, background_app, celery_session_worker, db_instance):
    make_and_login_user(client)
    add_training_objective(db_instance, date.today() - timedelta(5), date.today() + timedelta(1), 5)
    add_run(db_instance, date.today() - timedelta(4), 60 * 1000, 1)
    add_run(db_instance, date.today() - timedelta(3), 60 * 1000, 1)
    rv = client.get('/training_objectives')
    assert str(date.today() - timedelta(5)) in rv.data.decode('ascii')
    assert str(date.today() + timedelta(1)) in rv.data.decode('ascii')
    assert b'You can do it! Just 4.998 km!' in rv.data


def test_training_multiple_not_inside_the_objective(client, background_app, celery_session_worker, db_instance):
    make_and_login_user(client)
    add_training_objective(db_instance, date.today() - timedelta(5), date.today() + timedelta(1), 5)
    add_run(db_instance, date.today() + timedelta(2), 60 * 1000, 10000)
    add_run(db_instance, date.today() - timedelta(6), 60 * 1000, 10000)
    add_run(db_instance, date.today() - timedelta(3), 60 * 1000, 534)
    rv = client.get('/training_objectives')
    assert str(date.today() - timedelta(5)) in rv.data.decode('ascii')
    assert str(date.today() + timedelta(1)) in rv.data.decode('ascii')
    assert b'You can do it! Just 4.466 km!' in rv.data
