from unittest import mock
from monolith.database import User, Training_Objective
from tests.conftest import mocked_result
from flask import url_for
from datetime import date, timedelta, datetime

import json

def make_and_login_user(client):
  rv = client.post('/create_user', data=dict(submit='Publish', email='peppe@giro.it', firstname='peppe', lastname='p',
                                               password='peppe', age='1',
                                               weight='1', max_hr='1', rest_hr='1', vo2max='1'))
  rv = client.post('/login', data=dict(email='peppe@giro.it', password='peppe'), follow_redirects=True)

def test_create_training_with_non_authenticated_user(client, celery_session_worker, db_instance):
    rv = client.post('/training_objectives', data=dict(submit='Publish', start_date='2018-12-07', end_date='2018-12-07', kilometers_to_run='1'), follow_redirects=True)

    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 0
    assert rv.status_code == 200
    assert b'Hi Anonymous, <a href="/login">Log in</a> <a href="/create_user">Create user</a>' in rv.data

def test_create_training(client, db_instance):
    make_and_login_user(client)
    rv = client.post('/training_objectives', data=dict(submit='Publish', start_date='2018-12-07', end_date='2018-12-07', kilometers_to_run='1'),follow_redirects=True)
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 1
    assert rv.data.decode('ascii').count('2018-12-07') == 4
    assert b'          <td>2018-12-07</td>\n          <td>2018-12-07</td>'  in rv.data

def test_create_twice_same_training(client, db_instance):
    make_and_login_user(client)
    rv = client.post('/training_objectives', data=dict(submit='Publish', start_date='2018-12-07', end_date='2018-12-07', kilometers_to_run='1'),follow_redirects=True)
    rv = client.post('/training_objectives', data=dict(submit='Publish', start_date='2018-12-07', end_date='2018-12-07', kilometers_to_run='1'),follow_redirects=True)
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.start_date == '2018-12-07')
    assert r.count() == 2
    assert rv.data.decode('ascii').count('2018-12-07') == 6
    assert rv.data.decode('ascii').count('          <td>2018-12-07</td>\n          <td>2018-12-07</td>') == 2

def test_create_training_starts_yesterday(client, db_instance):
    make_and_login_user(client)
    yesterday = date.today() - timedelta(1)
    rv = client.post('/training_objectives', data=dict(submit='Publish', start_date=yesterday, end_date='2018-12-07', kilometers_to_run='1'),follow_redirects=True)
    assert rv.data.decode('ascii').count('2018-12-07') == 1
    assert rv.data.decode('ascii').count(str(yesterday)) == 1
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 0

def test_create_training_opposite_date(client, db_instance):
    make_and_login_user(client)
    rv = client.post('/training_objectives', data=dict(submit='Publish', start_date='2018-12-07', end_date='2018-11-07', kilometers_to_run='1'),follow_redirects=True)
    assert rv.data.decode('ascii').count('2018-12-07') == 1
    assert rv.data.decode('ascii').count('2018-11-07') == 1
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 0
    assert b'<p class="help-block">End date must not be less than Start date</p>' in rv.data

def test_create_training_ends_yesterday(client, db_instance):
    make_and_login_user(client)
    yesterday = date.today() - timedelta(1)
    rv = client.post('/training_objectives', data=dict(submit='Publish', start_date='2018-12-07', end_date=yesterday, kilometers_to_run='1'),follow_redirects=True)
    assert rv.data.decode('ascii').count('2018-12-07') == 1
    assert rv.data.decode('ascii').count('2018-11-07') == 1
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 0
    assert b'<p class="help-block">End date must not be less than Start date</p>' in rv.data
    assert b'<p class="help-block">End date must not be less than Start date</p>' in rv.data

def test_create_training_negative_km(client, db_instance):
    make_and_login_user(client)
    rv = client.post('/training_objectives', data=dict(submit='Publish', start_date='2018-12-07', end_date='2018-12-07', kilometers_to_run='-1'),follow_redirects=True)
    assert rv.data.decode('ascii').count('2018-12-07') == 2
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 0
