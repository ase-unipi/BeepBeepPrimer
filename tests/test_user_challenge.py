from unittest import mock
from monolith.database import User, Run, Challenge
from tests.conftest import mocked_result

# Test that checks if the create_user page permits to create 2 user with the same email
def test_create_challenge_without_run(client, db_instance, celery_session_worker):
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

    resp = client.post('/create_challenge',
        follow_redirects=True,
        data=dict(id_run='1'))

    assert resp.status_code == 200
    
    assert db_instance.session.query(Challenge).count() == 0
  