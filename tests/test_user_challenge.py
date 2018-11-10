from unittest import mock
from monolith.database import User, Run, Challenge
from tests.conftest import mocked_result
from flask import url_for
import pytest
import datetime


@pytest.fixture
def make_and_login_user(client, db_instance):
    response = client.post('/create_user', follow_redirects=True,
        data=dict(
            submit='Publish',
            email='1',
            firstname='1',
            lastname='1',
            password='1',
            age='1',
            weight='1',
            max_hr='1',
            rest_hr='1',
            vo2max='1'
        ))

    assert response.status_code == 200
    
    response = client.post('/login', follow_redirects=True, data=dict(email='1', password='1'))

    assert response.status_code == 200
    assert b'Hi 1!' in response.data
    assert b'Authorize Strava Access' in response.data

def createRun(
        db_instance,
        id,
        runner_id,
        distance = 1000,
        start_date = datetime.datetime.now().date(),
        elapsed_time = 3600,
        average_speed = 2):

    challenge_count = db_instance.session.query(Run).count()

    run = Run()
    run.id = id
    run.name = 'test run ' + str(run.id)
    run.strava_id = None
    run.distance = distance
    run.start_date = start_date
    run.elapsed_time =  elapsed_time
    run.average_speed = average_speed
    run.average_heartrate = None
    run.total_elevation_gain = 0
    run.runner_id = runner_id
    db_instance.session.add(run)

    assert db_instance.session.query(Run).count() == (challenge_count + 1)


def test_create_challenge_with_non_authenticated_user(client, db_instance, celery_session_worker):
    response = client.post('/create_challenge',
        follow_redirects=True,
        data=dict(id_run='1'))

    assert response.status_code == 200

    assert b'Hi Anonymous, <a href="/login">Log in</a> <a href="/create_user">Create user</a>' in response.data
    

def test_create_challenge_with_non_existing_run(client, db_instance, celery_session_worker, make_and_login_user):
    assert db_instance.session.query(Challenge).count() == 0

    response = client.post('/create_challenge',
        follow_redirects=True,
        data=dict(id_run='1'))

    assert response.status_code == 200

    assert b'Hi Anonymous, <a href="/login">Log in</a> <a href="/create_user">Create user</a>' not in response.data
    
    assert db_instance.session.query(Challenge).count() == 0
  

def test_visualize_non_existing_challenge(client, db_instance, celery_session_worker, make_and_login_user):
    
    response = client.get('/create_challenge/1', follow_redirects=True)
    assert b'Hi 1!' in response.data


def test_visualize_existing_challenge(client, db_instance, celery_session_worker, make_and_login_user):
    createRun(db_instance, 1, 1)

    client.post('/create_challenge',
        follow_redirects=True,
        data=dict(id_run='1'))
    assert db_instance.session.query(Challenge).count() == 1

    response = client.get('/create_challenge/1', follow_redirects=True)
    assert b'<h1>Challenge yourself!</h1>' in response.data


def test_create_correct_challenge(client, db_instance, celery_session_worker, make_and_login_user):
    
    # test_create_correct_challenge

    createRun(db_instance, id=1, runner_id=1, average_speed=2)


    client.post('/create_challenge',
        follow_redirects=True,
        data=dict(id_run='1'))
    assert db_instance.session.query(Challenge).count() == 1


    createRun(db_instance, id=2, runner_id=1, average_speed=3)

    client.post('/terminate_challenge',
        follow_redirects=True,
        data=dict(id_challenger='2', id_challenge=1))

    ch1 = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 2).first()
    assert ch1.run_challenger_id == 2
    assert ch1.result == True

    createRun(db_instance, id=3, runner_id=1, average_speed=1)

    client.post('/terminate_challenge',
        follow_redirects=True,
        data=dict(id_challenger='3', id_challenge=1))

    ch1 = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 3).first()
    assert ch1.run_challenger_id == 3
    assert ch1.result == False
    
    createRun(db_instance, id=4, runner_id=1, distance=2000)

    client.post('/terminate_challenge',
    follow_redirects=True,
    data=dict(id_challenger='4', id_challenge=1))

    ch1 = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 4).first()
    assert ch1.run_challenger_id == 4
    assert ch1.result

    createRun(db_instance, id=5, runner_id=1, distance=500)

    client.post('/terminate_challenge',
    follow_redirects=True,
    data=dict(id_challenger='5', id_challenge=1))

    ch1 = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 5).first()
    assert ch1.run_challenger_id == 5
    assert ch1.result == False

    createRun(db_instance, id=6, runner_id=1)

    client.post('/terminate_challenge',
    follow_redirects=True,
    data=dict(id_challenger='5', id_challenge=1))

    ch1 = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 5).first()
    assert ch1.run_challenger_id == 5
    assert ch1.result == False


def test_challenge_same_run(client, db_instance, celery_session_worker, make_and_login_user):

        # test_create_correct_challenge

    createRun(db_instance, id=1, runner_id=1, average_speed=2)

    client.post('/create_challenge',
        follow_redirects=True,
        data=dict(id_run='1'))
    assert db_instance.session.query(Challenge).count() == 1

    client.post('/terminate_challenge',
        follow_redirects=True,
        data=dict(id_challenger='1', id_challenge=1))

    assert db_instance.session.query(Challenge).count() == 1


def test_terminate_challenge_get(client, db_instance, celery_session_worker, make_and_login_user):
    
    response = client.get('/terminate_challenge', follow_redirects=True)
    assert b'<h1>Challenge yourself!</h1>' in response.data


def test_terminate_challenge_post_wrong_parameters(client, db_instance, celery_session_worker, make_and_login_user):

    #run and challenge not exist
    client.post('/terminate_challenge',
        follow_redirects=True,
        data=dict(id_challenger='2', id_challenge=1))

    assert db_instance.session.query(Challenge).count() == 0
    #challenger run not exists
    createRun(db_instance, id=1, runner_id=1, average_speed=2)
    client.post('/create_challenge',
        follow_redirects=True,
        data=dict(id_run='1'))

    ch1 = db_instance.session.query(Challenge).first()

    client.post('/terminate_challenge',
        follow_redirects=True,
        data=dict(id_challenger='2', id_challenge=1))

    assert db_instance.session.query(Challenge).count() == 1
    assert ch1.run_challenger_id == None

    #challenge not exists
    client.post('/terminate_challenge',
        follow_redirects=True,
        data=dict(id_challenger='1', id_challenge=2))

    assert db_instance.session.query(Challenge).count() == 1

