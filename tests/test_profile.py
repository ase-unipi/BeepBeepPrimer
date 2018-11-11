from unittest import mock
from monolith.database import User, Run
from tests.conftest import mocked_result


def make_and_login_user(client):
    rv = client.post('/create_user', data=dict(
                                                submit='Publish',
                                                email='peppe@giro.it',
                                                firstname='pappe', lastname='unique',
                                                password='password', age='1',
                                                weight='2',
                                                max_hr='3',
                                                rest_hr='4',
                                                vo2max='5'))
    rv = client.post('/login', data=dict(email='peppe@giro.it', password='password'), follow_redirects=True)


def test_profile(client, background_app, celery_session_worker):
    make_and_login_user(client)
    rv = client.get('/profile')
    print(rv.data.decode('ascii'))
    assert b'peppe@giro.it' in rv.data
    assert b'pappe' in rv.data
    assert b'unique' in rv.data
    assert b'YOUR OLD PASSWORD' in rv.data
    # assert b'Welcome pappe unique' in rv.data
    assert b'1' in rv.data
    assert b'2.0' in rv.data
    assert b'3' in rv.data
    assert b'4' in rv.data
    assert b'5.0' in rv.data


def test_update_profile_name(client, db_instance, background_app, celery_session_worker):
    make_and_login_user(client)
    rv = client.post('/profile', data=dict(submit='Publish', email='peppe@giro.it', firstname='papppe',
                                           lastname='unique', password='password', age='1', weight='2.0', max_hr='3',
                                           rest_hr='4', vo2max='5.0'))

    assert b'peppe@giro.it' in rv.data
    assert b'papppe' in rv.data
    assert b'unique' in rv.data
    assert b'YOUR OLD PASSWORD' in rv.data
    # assert b'Welcome pappe unique' in rv.data
    assert b'1' in rv.data
    assert b'2.0' in rv.data
    assert b'3' in rv.data
    assert b'4' in rv.data
    assert b'5.0' in rv.data
    u = db_instance.session.query(User).first()
    assert u.firstname == 'papppe'


def test_update_profile_surname(client, db_instance, background_app, celery_session_worker):
    make_and_login_user(client)
    rv = client.post('/profile', data=dict(submit='Publish', email='peppe@giro.it', firstname='papppe',
                                           lastname='not unique', password='password', age='1', weight='2.0', max_hr='3',
                                           rest_hr='4', vo2max='5.0'))

    assert b'peppe@giro.it' in rv.data
    assert b'papppe' in rv.data
    assert b'not unique' in rv.data
    assert b'YOUR OLD PASSWORD' in rv.data
    # assert b'Welcome pappe unique' in rv.data
    assert b'1' in rv.data
    assert b'2.0' in rv.data
    assert b'3' in rv.data
    assert b'4' in rv.data
    assert b'5.0' in rv.data
    u = db_instance.session.query(User).first()
    assert u.lastname == 'not unique'


def test_update_profile_password(client, db_instance, background_app, celery_session_worker):
    make_and_login_user(client)
    rv = client.post('/profile', data=dict(submit='Publish', email='peppe@giro.it', firstname='papppe',
                                           lastname='unique', password='pass', age='1', weight='2.0', max_hr='3',
                                           rest_hr='4', vo2max='5.0'))

    assert b'peppe@giro.it' in rv.data
    assert b'papppe' in rv.data
    assert b'unique' in rv.data
    assert b'YOUR OLD PASSWORD' in rv.data
    # assert b'Welcome pappe unique' in rv.data
    assert b'1' in rv.data
    assert b'2.0' in rv.data
    assert b'3' in rv.data
    assert b'4' in rv.data
    assert b'5.0' in rv.data
    u = db_instance.session.query(User).first()
    assert u.authenticate('pass')


def test_update_profile_age(client, db_instance, background_app, celery_session_worker):
    make_and_login_user(client)
    rv = client.post('/profile', data=dict(submit='Publish', email='peppe@giro.it', firstname='papppe',
                                           lastname='unique', password='password', age='6', weight='2.0', max_hr='3',
                                           rest_hr='4', vo2max='5.0'))

    assert b'peppe@giro.it' in rv.data
    assert b'papppe' in rv.data
    assert b'unique' in rv.data
    assert b'YOUR OLD PASSWORD' in rv.data
    # assert b'Welcome pappe unique' in rv.data
    assert b'6' in rv.data
    assert b'2.0' in rv.data
    assert b'3' in rv.data
    assert b'4' in rv.data
    assert b'5.0' in rv.data
    u = db_instance.session.query(User).first()
    assert u.age == 6


def test_update_profile_weight(client, db_instance, background_app, celery_session_worker):
    make_and_login_user(client)
    rv = client.post('/profile', data=dict(submit='Publish', email='peppe@giro.it', firstname='papppe',
                                           lastname='unique', password='password', age='1', weight='2.5', max_hr='3',
                                           rest_hr='4', vo2max='5.0'))

    assert b'peppe@giro.it' in rv.data
    assert b'papppe' in rv.data
    assert b'unique' in rv.data
    assert b'YOUR OLD PASSWORD' in rv.data
    # assert b'Welcome pappe unique' in rv.data
    assert b'1' in rv.data
    assert b'2.5' in rv.data
    assert b'3' in rv.data
    assert b'4' in rv.data
    assert b'5.0' in rv.data
    u = db_instance.session.query(User).first()
    assert u.weight == 2.5


def test_update_profile_max_hr(client, db_instance, background_app, celery_session_worker):
    make_and_login_user(client)
    rv = client.post('/profile', data=dict(submit='Publish', email='peppe@giro.it', firstname='papppe',
                                           lastname='unique', password='password', age='1', weight='2.0', max_hr='6',
                                           rest_hr='4', vo2max='5.0'))

    assert b'peppe@giro.it' in rv.data
    assert b'papppe' in rv.data
    assert b'unique' in rv.data
    assert b'YOUR OLD PASSWORD' in rv.data
    # assert b'Welcome pappe unique' in rv.data
    assert b'1' in rv.data
    assert b'2.0' in rv.data
    assert b'6' in rv.data
    assert b'4' in rv.data
    assert b'5.0' in rv.data
    u = db_instance.session.query(User).first()
    assert u.max_hr == 6


def test_update_profile_rest_hr(client, db_instance, background_app, celery_session_worker):
    make_and_login_user(client)
    rv = client.post('/profile', data=dict(submit='Publish', email='peppe@giro.it', firstname='papppe',
                                           lastname='unique', password='password', age='1', weight='2.0', max_hr='3',
                                           rest_hr='6', vo2max='5.0'))

    assert b'peppe@giro.it' in rv.data
    assert b'papppe' in rv.data
    assert b'unique' in rv.data
    assert b'YOUR OLD PASSWORD' in rv.data
    # assert b'Welcome pappe unique' in rv.data
    assert b'1' in rv.data
    assert b'2.0' in rv.data
    assert b'3' in rv.data
    assert b'6' in rv.data
    assert b'5.0' in rv.data
    u = db_instance.session.query(User).first()
    assert u.rest_hr == 6


def test_update_profile_vo2max(client, db_instance, background_app, celery_session_worker):
    make_and_login_user(client)
    rv = client.post('/profile', data=dict(submit='Publish', email='peppe@giro.it', firstname='papppe',
                                           lastname='unique', password='password', age='1', weight='2.0', max_hr='3',
                                           rest_hr='4', vo2max='6'))

    assert b'peppe@giro.it' in rv.data
    assert b'papppe' in rv.data
    assert b'unique' in rv.data
    assert b'YOUR OLD PASSWORD' in rv.data
    # assert b'Welcome pappe unique' in rv.data
    assert b'1' in rv.data
    assert b'2.0' in rv.data
    assert b'3' in rv.data
    assert b'4' in rv.data
    assert b'6' in rv.data
    u = db_instance.session.query(User).first()
    assert u.vo2max == 6




