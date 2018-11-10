from unittest import mock
from monolith.database import User, Training_Objective, Run
from tests.conftest import mocked_result
from flask import url_for
from datetime import date, timedelta, datetime
from sqlalchemy import func
import json

YESTERDAY = date.today() - timedelta(1)
TODAY = date.today()
id_run = 1
# Creates and performs the login of one user
def make_and_login_user(client, email = 'peppe@giro.it'):
    rv = client.post('/create_user', data=dict(
        										submit='Publish', 
        										email=email, 
        										firstname='peppe', 
        										lastname='p',
        										password='peppe', age='1',
        										weight='1', 
        										max_hr='1', 
        										rest_hr='1', 
        										vo2max='1'))
    rv = client.post('/login', data=dict(email='peppe@giro.it', password='peppe'), follow_redirects=True)

def add_training_objective(db, start, finish, km, user=None):
    if user is None:
        user = db.session.query(User).first()
    t = Training_Objective(start_date=start, end_date=finish, kilometers_to_run=km, runner_id=user.id)
    db.session.add(t)
    db.session.commit()

def add_run(db, start, time, km, user=None):
    global id_run
    if user is None:
        user = db.session.query(User).first()
    r = Run(name="run", strava_id=id_run, distance=km, start_date=start, elapsed_time=time,
            average_speed=10, average_heartrate=0, total_elevation_gain=0, runner_id=user.id)
    id_run += 1
    db.session.add(r)
    db.session.commit()

# Checks if a specific training has been completed
def check_completed_distance_one_user(db_instance, training_id = 1):
    t = db_instance.session.query(Training_Objective).filter(Training_Objective.id == training_id)
    assert t.count() == 1
    run = db_instance.session.query(
        func.sum(Run.distance).label('total_distance')).first()
    return t.first().kilometers_to_run*1000 <= run.total_distance

# Tests if the training objective page is accessible for a non authenticated user
def test_access_training_with_non_authenticated_user(client, celery_session_worker, db_instance):
    rv = client.get('/training_objectives', follow_redirects=True)
    assert b'Hi Anonymous, <a href="/login">Log in</a> <a href="/create_user">Create user</a>' in rv.data

# For past trainig objectives
# Test the behavior for a completed training objective done in the past
def test_get_past_completed_training(client, background_app, db_instance, celery_session_worker):
    run_date = TODAY - timedelta(2)
    start_date_training = TODAY - timedelta(3)
    end_date_training = YESTERDAY
    make_and_login_user(client)
    add_run(db_instance, run_date, 60*1000, 2000)
    add_training_objective(db_instance, start_date_training, end_date_training, 1)    
    assert check_completed_distance_one_user(db_instance)
    rv = client.get('/training_objectives', follow_redirects=True)
    assert b'              <img class="icon" src="/static/check.png"/>' in rv.data

# Test the behavior for a failed training objective done in the past
def test_get_past_failed_training(client, background_app, db_instance, celery_session_worker):
    make_and_login_user(client)
    add_training_objective(db_instance, YESTERDAY, YESTERDAY, 1)
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 1
    assert db_instance.session.query(Run).count() == 0
    rv = client.get('/training_objectives', follow_redirects=True)
    assert b'              <img class="icon" src="/static/cross.png"/>' in rv.data

#For future trainig objectives
# Test the behavior for a completed training objective done in the future
def test_get_future_completed_training(client, background_app, db_instance, celery_session_worker):
    make_and_login_user(client)
    add_run(db_instance, (TODAY+timedelta(1)), 60*1000, 2000)
    end_date = date.today() + timedelta(2)
    rv = client.post('/training_objectives', data=dict(submit='Publish', start_date=TODAY, end_date=end_date, kilometers_to_run='1'),follow_redirects=True)
    assert rv.data.decode('ascii').count(str(TODAY)) == 2
    assert rv.data.decode('ascii').count(str(end_date)) == 2
    assert check_completed_distance_one_user(db_instance)
    rv = client.get('/training_objectives', follow_redirects=True)
    assert b'              <img class="icon" src="/static/check.png"/>' in rv.data

#For present training objectives
# Test the behavior for an active training objective
def test_get_active_training(client, background_app, db_instance, celery_session_worker):
    make_and_login_user(client)
    add_run(db_instance, (TODAY + timedelta(1)), 60*1000, 2000)
    end_date = TODAY + timedelta(2)
    rv = client.post('/training_objectives', data=dict(submit='Publish', start_date=TODAY, end_date=end_date, kilometers_to_run='100000'),follow_redirects=True)
    assert rv.data.decode('ascii').count(str(TODAY)) == 2
    assert rv.data.decode('ascii').count(str(end_date)) == 2
    rv = client.get('/training_objectives', follow_redirects=True)
    assert b'              <img class="icon" src="/static/circle.png"/>' in rv.data
    assert not(check_completed_distance_one_user(db_instance))

# Test the behavior for a completed training objective in one day
def test_get_completed_in_one_day(client, background_app, db_instance, celery_session_worker):
	make_and_login_user(client)
	add_run(db_instance, TODAY, 60*1000, 2000)
	rv = client.post('/training_objectives', data=dict(submit='Publish', start_date=TODAY, end_date=TODAY, kilometers_to_run='1'),follow_redirects=True)
	assert rv.data.decode('ascii').count(str(TODAY)) == 4
	assert check_completed_distance_one_user(db_instance)
	rv = client.get('/training_objectives', follow_redirects=True)
	assert b'              <img class="icon" src="/static/check.png"/>' in rv.data

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

# Tets that the program respects the training objectives of the different users
def test_get_from_correct_user(client, background_app, db_instance, celery_session_worker):
	make_and_login_user(client)
	user = db_instance.session.query(User).filter(User.id == 1).first()
	add_training_objective(db_instance, TODAY, TODAY+timedelta(1), 26, user)
	add_run(db_instance, TODAY, 60 * 1000, 20000, user)
	client.get('/logout', follow_redirects=True)
	make_and_login_user(client,'peppino@giro.it')
	user = db_instance.session.query(User).filter(User.id == 2).first()
	add_training_objective(db_instance, TODAY, TODAY+timedelta(1), 26, user)
	add_run(db_instance, TODAY, 60 * 1000, 20000, user)
	rv = client.get('/training_objectives', follow_redirects=True)
	t = db_instance.session.query(Training_Objective).filter(Training_Objective.runner_id == user.id)
	km_to_run_enconde = str(t.first().kilometers_to_run).encode('ascii', 'ignore')
	km_runned_encode = str(db_instance.session.query(Run).filter(Run.runner_id == user.id).first().distance/1000).encode('ascii', 'ignore')
	print(rv.data)
	assert b'          <td>%s</td>\n          <td>%s</td>' %(km_to_run_enconde, km_runned_encode)  in rv.data


