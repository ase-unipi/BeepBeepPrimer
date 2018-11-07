from unittest import mock
from monolith.database import User, Run, Challenge
from tests.conftest import mocked_result
from flask import url_for

def test_create_challenge_with_non_authenticated_user(client, db_instance, celery_session_worker):
    response = client.post('/create_challenge',
        follow_redirects=True,
        data=dict(id_run='1'))

    assert response.status_code == 200

    assert b'Hi Anonymous, <a href="/login">Log in</a> <a href="/create_user">Create user</a>' in response.data
    

def test_create_challenge_with_non_existing_run(client, db_instance, celery_session_worker):
    client.post('/create_user', follow_redirects=True,
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

    client.post('/login', follow_redirects=True, data=dict(email='1', password='1'))

    assert db_instance.session.query(Challenge).count() == 0

    response = client.post('/create_challenge',
        follow_redirects=True,
        data=dict(id_run='1'))

    assert response.status_code == 200
    
    # assert db_instance.session.query(Challenge).count() == 0
  