from unittest import mock
from monolith.database import User, Run, Challenge
from tests.conftest import mocked_result
from flask import render_template
import pytest
import datetime


@pytest.fixture
def make_and_login_user(client, db_instance):
    response = client.post('/create_user', follow_redirects=True, data=dict(
        submit='Publish',
        email='test@email.com',
        firstname='1',
        lastname='1',
        password='1',
        age='1',
        weight='1',
        max_hr='1',
        rest_hr='1',
        vo2max='1'))

    assert response.status_code == 200
    print(response.data.decode('ascii'))
    assert b'> Please Login or Register </' in response.data

    response = client.post('/login', follow_redirects=True, data=dict(email='test@email.com', password='1'))
    assert response.status_code == 200
    print(response.data.decode('ascii'))
    assert b'>Hi test@email.com </' in response.data

def createRun(
        db_instance,
        id_,
        runner_id,
        distance=1000,
        start_date=datetime.datetime(year=2018, month=1, day=1),
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


def test_non_authenticated_user(client, db_instance, celery_session_worker):
    login = b'<a href="/login">Log in</a>'
    redirecting = b'<h1>Redirecting...</h1>'

    response = client.get('/create_challenge')
    print(response.data.decode('ascii'))
    assert response.status_code == 200 or response.status_code == 302
    assert login or redirecting in response.data

    response = client.get('/create_challenge/1')
    print(response.data.decode('ascii'))
    assert response.status_code == 200 or response.status_code == 302
    assert login or redirecting in response.data

    response = client.post('/create_challenge')
    print(response.data.decode('ascii'))
    assert response.status_code == 200 or response.status_code == 302
    assert login or redirecting in response.data

    response = client.get('/terminate_challenge')
    print(response.data.decode('ascii'))
    assert response.status_code == 200 or response.status_code == 302
    assert login or redirecting in response.data

    response = client.post('/terminate_challenge')
    print(response.data.decode('ascii'))
    assert response.status_code == 200 or response.status_code == 302
    assert login or redirecting in response.data


def test_create_challenge_get(client, db_instance, celery_session_worker, make_and_login_user):
    response = client.get('/create_challenge', follow_redirects=True)
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data


def test_create_challenge_post_wrong_parameter(client, db_instance, celery_session_worker, make_and_login_user):
    assert db_instance.session.query(Challenge).count() == 0

    response = client.post('/create_challenge',
                           follow_redirects=True,
                           data=dict(id_run='1'))
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'Hi Anonymous, <a href="/login">Log in</a> <a href="/create_user">Create user</a>' not in response.data

    assert db_instance.session.query(Challenge).count() == 0


def test_create_challenge_post_good_parameter(client, db_instance, celery_session_worker, make_and_login_user):
    createRun(db_instance, id_=1, runner_id=1)
    createRun(db_instance, id_=2, runner_id=1)
    createRun(db_instance, id_=3, runner_id=1,
              start_date=datetime.datetime.today() - datetime.timedelta(days=1))
    createRun(db_instance, id_=4, runner_id=1,
              start_date=datetime.datetime.today() + datetime.timedelta(days=1))

    assert db_instance.session.query(Challenge).count() == 0

    response = client.post('/create_challenge',
                           follow_redirects=True,
                           data=dict(id_run='1'))
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 1</td>' in response.data
    assert b'>test run 2</' not in response.data
    assert b'>test run 3</' not in response.data
    assert b'>test run 4</' in response.data

    assert db_instance.session.query(Challenge).count() == 1
    assert db_instance.session.query(Challenge).filter(Challenge.run_challenged_id == 1).count() == 1

    response = client.post('/create_challenge',
                           follow_redirects=True,
                           data=dict(id_run='2'))
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 2</td>' in response.data
    assert b'>test run 1</' not in response.data
    assert b'>test run 3</' not in response.data
    assert b'>test run 4</' in response.data

    assert db_instance.session.query(Challenge).count() == 2
    assert db_instance.session.query(Challenge).filter(Challenge.run_challenged_id == 1).count() == 1


    response = client.post('/create_challenge',
                           follow_redirects=True,
                           data=dict(id_run='3'))
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 3</td>' in response.data
    assert b'>test run 1</' not in response.data
    assert b'>test run 2</' not in response.data
    assert b'>test run 4</' in response.data

    assert db_instance.session.query(Challenge).count() == 3
    assert db_instance.session.query(Challenge).filter(Challenge.run_challenged_id == 1).count() == 1


    response = client.post('/create_challenge',
                           follow_redirects=True,
                           data=dict(id_run='4'))
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 4</td>' in response.data
    assert b'>test run 1</' not in response.data
    assert b'>test run 2</' not in response.data
    assert b'>test run 3</' not in response.data

    assert db_instance.session.query(Challenge).count() == 4
    assert db_instance.session.query(Challenge).filter(Challenge.run_challenged_id == 1).count() == 1


def test_create_challenge_id_challenge_get_wrong_resource(client, db_instance, celery_session_worker, make_and_login_user):
    response = client.get('/create_challenge/1', follow_redirects=True)
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Hi test@email.com </' in response.data


def test_create_challenge_id_challenge_get_good_resource(client, db_instance, celery_session_worker, make_and_login_user):
    createRun(db_instance, id_=1, runner_id=1)
    createRun(db_instance, id_=2, runner_id=1)
    createRun(db_instance, id_=3, runner_id=1,
              start_date=datetime.datetime.today() - datetime.timedelta(days=1))
    createRun(db_instance, id_=4, runner_id=1,
              start_date=datetime.datetime.today() + datetime.timedelta(days=1))

    client.post('/create_challenge',
                follow_redirects=True,
                data=dict(id_run='1'))
    client.post('/create_challenge',
                follow_redirects=True,
                data=dict(id_run='2'))
    client.post('/create_challenge',
                follow_redirects=True,
                data=dict(id_run='3'))
    client.post('/create_challenge',
                follow_redirects=True,
                data=dict(id_run='4'))


    response = client.get('/create_challenge/1', follow_redirects=True)
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 1</td>' in response.data
    assert b'>test run 2</' not in response.data
    assert b'>test run 3</' not in response.data
    assert b'>test run 4</' in response.data

    response = client.get('/create_challenge/2', follow_redirects=True)
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 2</td>' in response.data
    assert b'>test run 1</' not in response.data
    assert b'>test run 3</' not in response.data
    assert b'>test run 4</' in response.data

    response = client.get('/create_challenge/3', follow_redirects=True)
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 3</td>' in response.data
    assert b'>test run 1</' not in response.data
    assert b'>test run 2</' not in response.data
    assert b'>test run 4</' in response.data

    response = client.get('/create_challenge/4', follow_redirects=True)
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 4</td>' in response.data
    assert b'>test run 1</' not in response.data
    assert b'>test run 2</' not in response.data
    assert b'>test run 3</' not in response.data


def test_terminate_challenge_get(client, db_instance, celery_session_worker, make_and_login_user):
    response = client.get('/terminate_challenge', follow_redirects=True)
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'>Create a new challenge</' in response.data


def test_terminate_challenge_post_wrong_parameters(client, db_instance, celery_session_worker, make_and_login_user):

    response = client.post('/terminate_challenge',
                           follow_redirects=True,
                           data=dict(id_challenger='2', id_challenge=1))
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'>Create a new challenge</' in response.data

    assert db_instance.session.query(Challenge).count() == 0
    createRun(db_instance, id_=1, runner_id=1, average_speed=2)
    response = client.post('/create_challenge',
                           follow_redirects=True,
                           data=dict(id_run='1'))
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 1</td>' in response.data

    ch1 = db_instance.session.query(Challenge).first()

    response = client.post('/terminate_challenge',
                           follow_redirects=True,
                           data=dict(id_challenger='2', id_challenge=1))
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'>Create a new challenge</' in response.data

    assert db_instance.session.query(Challenge).count() == 1
    assert ch1.run_challenger_id is None

    #challenge not exists
    response = client.post('/terminate_challenge',
                           follow_redirects=True,
                           data=dict(id_challenger='1', id_challenge=2))
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'>Create a new challenge</' in response.data

    assert db_instance.session.query(Challenge).count() == 1

    #challenge same run
    response = client.post('/terminate_challenge',
                           follow_redirects=True,
                           data=dict(id_challenger='1', id_challenge=1))
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'>Create a new challenge</' in response.data

    assert db_instance.session.query(Challenge).count() == 1

    # challenge previous run
    createRun(db_instance, id_=2, runner_id=1, average_speed=3,
              start_date=datetime.datetime.today() - datetime.timedelta(days=1))

    response = client.post('/terminate_challenge',
                           follow_redirects=True,
                           data=dict(id_challenger='2', id_challenge=1))
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'>Create a new challenge</' in response.data

    assert db_instance.session.query(Challenge).count() == 1
    assert db_instance.session\
            .query(Challenge)\
            .filter(Challenge.id == 1)\
            .filter(Challenge.run_challenger_id == 2)\
            .count() == 0


def test_terminate_challenge_post_good_parameter_result(client, db_instance, celery_session_worker, make_and_login_user):
    createRun(db_instance, id_=1, runner_id=1, average_speed=2)
    createRun(db_instance, id_=2, runner_id=1, average_speed=3,
              start_date=datetime.datetime.today() + datetime.timedelta(days=1))
    createRun(db_instance, id_=3, runner_id=1, average_speed=1,
              start_date=datetime.datetime.today() + datetime.timedelta(days=1))
    createRun(db_instance, id_=4, runner_id=1, distance=2000,
              start_date=datetime.datetime.today() + datetime.timedelta(days=1))
    createRun(db_instance, id_=5, runner_id=1, distance=500,
              start_date=datetime.datetime.today() + datetime.timedelta(days=1))
    createRun(db_instance, id_=6, runner_id=1,
              start_date=datetime.datetime.today() + datetime.timedelta(days=1))

    for _ in range(1, 6):
        client.post('/create_challenge',
                    follow_redirects=True,
                    data=dict(id_run='1'))

    response = client.post('/terminate_challenge',
                           follow_redirects=True,
                           data=dict(id_challenge=1, id_challenger=2))
    query_result = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 2).first()
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 1</td>' in response.data
    assert b'test run 2' in response.data
    assert b'test run 3' not in response.data
    assert b'test run 4' not in response.data
    assert b'test run 5' not in response.data
    assert b'test run 6' not in response.data

    assert query_result.run_challenger_id == 2
    assert query_result.result is True


    response = client.post('/terminate_challenge',
                           follow_redirects=True,
                           data=dict(id_challenge=2, id_challenger=3))
    query_result = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 3).first()
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 1</td>' in response.data
    assert b'test run 2' not in response.data
    assert b'test run 3' in response.data
    assert b'test run 4' not in response.data
    assert b'test run 5' not in response.data
    assert b'test run 6' not in response.data

    assert query_result.run_challenger_id == 3
    assert query_result.result is False


    response = client.post('/terminate_challenge',
                           follow_redirects=True,
                           data=dict(id_challenge=3, id_challenger=4))
    query_result = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 4).first()
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 1</td>' in response.data
    assert b'test run 2' not in response.data
    assert b'test run 3' not in response.data
    assert b'test run 4' in response.data
    assert b'test run 5' not in response.data
    assert b'test run 6' not in response.data

    assert query_result.run_challenger_id == 4
    assert query_result.result


    response = client.post('/terminate_challenge',
                           follow_redirects=True,
                           data=dict(id_challenge=4, id_challenger=5))
    query_result = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 5).first()
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 1</td>' in response.data
    assert b'test run 2' not in response.data
    assert b'test run 3' not in response.data
    assert b'test run 4' not in response.data
    assert b'test run 5' in response.data
    assert b'test run 6' not in response.data

    assert query_result.run_challenger_id == 5
    assert query_result.result is False


    response = client.post('/terminate_challenge',
                           follow_redirects=True,
                           data=dict(id_challenge=5, id_challenger=6))
    query_result = db_instance.session.query(Challenge).filter(Challenge.run_challenger_id == 6).first()
    print(response.data.decode('ascii'))
    assert response.status_code == 200
    assert b'>Challenge yourself!</' in response.data
    assert b'<td class="text-center header" style="width: 48%;">test run 1</td>' in response.data
    assert b'test run 2' not in response.data
    assert b'test run 3' not in response.data
    assert b'test run 4' not in response.data
    assert b'test run 5' not in response.data
    assert b'test run 6' in response.data

    assert query_result.run_challenger_id == 6
    assert query_result.result is False
