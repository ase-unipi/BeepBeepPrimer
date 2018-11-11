from unittest import mock
from monolith.database import User, Training_Objective
from tests.conftest import mocked_result
from flask import url_for
from datetime import date, timedelta, datetime
import json

start_end_date = date.today()

def make_and_login_user(client):
  rv = client.post('/create_user', data=dict(
                                                submit='Publish', 
                                                email='peppe@giro.it', 
                                                firstname='peppe', lastname='p',
                                                password='peppe', age='1',
                                                weight='1', 
                                                max_hr='1', 
                                                rest_hr='1',
                                                vo2max='1'))
  rv = client.post('/login', data=dict(email='peppe@giro.it', password='peppe'), follow_redirects=True)

def create_training_objective(client, db_instance, start_date = date.today(), end_date = date.today(), km = 1):
    return client.post('/training_objectives', data=dict(
                                                        submit='Publish', 
                                                        start_date=start_date, 
                                                        end_date=end_date, 
                                                        kilometers_to_run=km),
                                             follow_redirects=True)

def test_create_training_with_non_authenticated_user(client, celery_session_worker, db_instance):
    rv = create_training_objective(client, db_instance)
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 0
    assert rv.status_code == 200
    assert b'Hi Anonymous, <a href="/login">Log in</a> <a href="/create_user">Create user</a>' in rv.data

def test_create_training(client, background_app, db_instance):
    make_and_login_user(client)
    rv = create_training_objective(client, db_instance)
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 1
    assert rv.data.decode('ascii').count(str(start_end_date)) == 4
    converted_date = (str(start_end_date)).encode('ascii', 'ignore')
    assert b'          <td>%s</td>\n          <td>%s</td>' %(converted_date, converted_date)  in rv.data

def test_create_twice_same_training(client, background_app, db_instance):
    make_and_login_user(client)
    start_end_date = date.today()
    rv = create_training_objective(client, db_instance)
    rv = create_training_objective(client, db_instance)
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.start_date == str(start_end_date))
    assert r.count() == 2
    assert rv.data.decode('ascii').count(str(start_end_date)) == 6
    converted_date = (str(start_end_date)).encode('ascii', 'ignore')
    assert rv.data.decode('ascii').count('          <td>%s</td>\n          <td>%s</td>' % (str(start_end_date), str(start_end_date))) == 2

def test_create_training_starts_yesterday(client, background_app, db_instance):
    make_and_login_user(client)
    today = date.today()
    yesterday = date.today() - timedelta(1)
    rv = create_training_objective(client, db_instance, yesterday, today)
    assert rv.data.decode('ascii').count(str(today)) == 1
    assert rv.data.decode('ascii').count(str(yesterday)) == 1
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 0

def test_create_training_opposite_date(client, background_app, db_instance):
    make_and_login_user(client)
    end_date = date.today() + timedelta(1)
    start_date = date.today() + timedelta(3)
    rv = create_training_objective(client, db_instance, start_date, end_date)
    assert rv.data.decode('ascii').count(str(start_date)) == 1
    assert rv.data.decode('ascii').count(str(end_date)) == 1
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 0
    assert b'<p class="help-block">End date must not be less than Start date</p>' in rv.data

def test_create_training_ends_yesterday(client, background_app, db_instance):
    make_and_login_user(client)
    yesterday = date.today() - timedelta(1)
    start_date = date.today() + timedelta(1)
    rv = create_training_objective(client, db_instance, start_date, yesterday)
    assert rv.data.decode('ascii').count(str(start_date)) == 1
    assert rv.data.decode('ascii').count(str(yesterday)) == 1
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 0
    assert b'<p class="help-block">End date must not be less than Start date</p>' in rv.data
    assert b'<p class="help-block">End date must not be less than Start date</p>' in rv.data

def test_create_training_negative_km(client, background_app, db_instance):
    make_and_login_user(client)
    start_end_date = date.today()
    rv = create_training_objective(client, db_instance, start_end_date, start_end_date, -1)
    assert rv.data.decode('ascii').count(str(start_end_date)) == 2
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 0

def test_correct_assigning_training_runner(client, background_app, db_instance):
    client.post('/create_user', data=dict(
                                            submit='Publish', 
                                            email='peppino@giro.it', 
                                            firstname='peppino', 
                                            lastname='p',
                                            password='peppino', 
                                            age='1',
                                            weight='1', 
                                            max_hr='1', 
                                            rest_hr='1', 
                                            vo2max='1'))

    client.post('/login', data=dict(email='peppino@giro.it', password='peppino'), follow_redirects=True)
    client.post('/training_objectives', data=dict(
                                                    submit='Publish', 
                                                    start_date=start_end_date, 
                                                    end_date=start_end_date, 
                                                    kilometers_to_run='1'),
                                        follow_redirects=True)
    client.get('/logout', follow_redirects=True)
    make_and_login_user(client)
    rv = create_training_objective(client, db_instance, start_end_date, start_end_date)
    r = db_instance.session.query(Training_Objective).filter(Training_Objective.id == 1)
    assert r.count() == 1