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
        id_,
        runner_id,
        distance=1000,
        start_date=datetime.datetime.now().date(),
        elapsed_time=3600,
        average_speed=2):

    run_count = db_instance.session.query(Run).count()

    run = Run()
    run.id = id_
    run.name = 'test run ' + str(run.id)
    run.strava_id = None
    run.distance = distance
    run.start_date = start_date
    run.elapsed_time = elapsed_time
    run.average_speed = average_speed
    run.average_heartrate = None
    run.total_elevation_gain = 0
    run.runner_id = runner_id
    db_instance.session.add(run)

    assert db_instance.session.query(Run).count() == (run_count + 1)


def test_create_challenge_with_non_authenticated_user(client, db_instance, celery_session_worker):
    response = client.post('/create_challenge',
                           follow_redirects=True,
                           data=dict(id_run='1'))

    assert response.status_code == 200

    assert b'Hi Anonymous, <a href="/login">Log in</a> <a href="/create_user">Create user</a>' in response.data


def test_visualize_existing_challenge(client, db_instance, celery_session_worker, make_and_login_user):
    createRun(db_instance, id_=1, runner_id=1)

    client.post('/create_challenge',
                follow_redirects=True,
                data=dict(id_run='1'))
    assert db_instance.session.query(Challenge).count() == 1

    response = client.get('/create_challenge/1', follow_redirects=True)
    assert b'<h1>Challenge yourself!</h1>' in response.data


def test_create_challenge_get(client, db_instance, celery_session_worker, make_and_login_user):
    response = client.get('/create_challenge', follow_redirects=True)
    assert b'<h1>Challenge yourself!</h1>' in response.data


def test_create_challenge_post_wrong_parameter(client, db_instance, celery_session_worker, make_and_login_user):
    assert db_instance.session.query(Challenge).count() == 0

    response = client.post('/create_challenge',
                           follow_redirects=True,
                           data=dict(id_run='1'))

    assert response.status_code == 200

    assert b'Hi Anonymous, <a href="/login">Log in</a> <a href="/create_user">Create user</a>' not in response.data

    assert db_instance.session.query(Challenge).count() == 0


def test_create_challenge_post_good_parameter(client, db_instance, celery_session_worker, make_and_login_user):
    createRun(db_instance, id_=1, runner_id=1)
    createRun(db_instance, id_=10, runner_id=1)

    assert db_instance.session.query(Challenge).count() == 0

    client.post('/create_challenge',
                follow_redirects=True,
                data=dict(id_run='1'))
    assert db_instance.session.query(Challenge).count() == 1
    assert db_instance.session.query(Challenge).filter(Challenge.run_challenged_id == 1).count() == 1


    client.post('/create_challenge',
                follow_redirects=True,
                data=dict(id_run='10'))
    assert db_instance.session.query(Challenge).count() == 2
    assert db_instance.session.query(Challenge).filter(Challenge.run_challenged_id == 10).count() == 1


def test_create_challenge_id_challenge_get_wrong_resource(client, db_instance, celery_session_worker, make_and_login_user):
    response = client.get('/create_challenge/1', follow_redirects=True)
    assert b'Hi 1!' in response.data


def test_create_challenge_id_challenge_get_good_resource(client, db_instance, celery_session_worker, make_and_login_user):
    createRun(db_instance, id_=1, runner_id=1)
    createRun(db_instance, id_=2, runner_id=1)

    client.post('/create_challenge',
                follow_redirects=True,
                data=dict(id_run='1'))

    r = client.post('/create_challenge',
                    follow_redirects=True,
                    data=dict(id_run='2'))
    print(r.data.decode('ascii'))


    response = client.get('/create_challenge/1', follow_redirects=True)
    assert b'<h1>Challenge yourself!</h1>' in response.data

    response = client.get('/create_challenge/2', follow_redirects=True)
    assert b'<h1>Challenge yourself!</h1>' in response.data


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
    createRun(db_instance, id_=1, runner_id=1, average_speed=2)
    client.post('/create_challenge',
                follow_redirects=True,
                data=dict(id_run='1'))

    ch1 = db_instance.session.query(Challenge).first()

    client.post('/terminate_challenge',
                follow_redirects=True,
                data=dict(id_challenger='2', id_challenge=1))

    assert db_instance.session.query(Challenge).count() == 1
    assert ch1.run_challenger_id is None

    #challenge not exists
    client.post('/terminate_challenge',
                follow_redirects=True,
                data=dict(id_challenger='1', id_challenge=2))

    assert db_instance.session.query(Challenge).count() == 1

    #challenge same run
    client.post('/terminate_challenge',
                follow_redirects=True,
                data=dict(id_challenger='1', id_challenge=1))

    assert db_instance.session.query(Challenge).count() == 1


def test_create_correct_challenge(client, db_instance, celery_session_worker, make_and_login_user):
    createRun(db_instance, id_=1, runner_id=1, average_speed=2)
    createRun(db_instance, id_=2, runner_id=1, average_speed=3)
    createRun(db_instance, id_=3, runner_id=1, average_speed=1)
    createRun(db_instance, id_=4, runner_id=1, distance=2000)
    createRun(db_instance, id_=5, runner_id=1, distance=500)
    createRun(db_instance, id_=6, runner_id=1)

    for i in range(1, 6):
        client.post('/create_challenge',
                    follow_redirects=True,
                    data=dict(id_run='1'))

        client.post('/terminate_challenge',
                    follow_redirects=True,
                    data=dict(id_challenge=i, id_challenger=str(i+1)))


    query_result = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 2).first()
    assert query_result.run_challenger_id == 2
    assert query_result.result is True

    query_result = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 3).first()
    assert query_result.run_challenger_id == 3
    assert query_result.result is False

    query_result = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 4).first()
    assert query_result.run_challenger_id == 4
    assert query_result.result

    query_result = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 5).first()
    assert query_result.run_challenger_id == 5
    assert query_result.result is False

    query_result = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 6).first()
    assert query_result.run_challenger_id == 6
    assert query_result.result is False
