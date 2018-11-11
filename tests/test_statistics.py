import os
from unittest import mock
from monolith.database import User, Training_Objective, Run
from tests.conftest import mocked_result
from flask import url_for, g
from datetime import date, timedelta, datetime
from sqlalchemy import func
import json
from monolith.views.statistics import concatenate_run_name_id, PLOTS_DIRECTORY, PLOTS_FORMAT
from flask_login import current_user


id_run  = 0
id_user = 1
ROUTE_LOGIN      = '/login'
ROUTE_STATISTICS = '/statistics'
ROUTE_LOGOUT     = '/logout'

dates = dict(yesterday = datetime.today() - timedelta(days = -1),
             today     = datetime.today() - timedelta(days =  0),
             tomorrow  = datetime.today() - timedelta(days =  1))

USER_ONE = dict(submit    = 'Publish', 
                email     = 'ase@ase.it', 
                firstname = 'ase',
                lastname  = 'ase',
                password  = 'ase',
                age       = '1',
                weight    = '1', 
                max_hr    = '1', 
                rest_hr   = '1',
                vo2max    = '1')

USER_TWO = dict(submit    = 'Publish', 
                email     = 'ase2@ase.it', 
                firstname = 'ase',
                lastname  = 'ase',
                password  = 'ase',
                age       = '1',
                weight    = '1', 
                max_hr    = '1', 
                rest_hr   = '1',
                vo2max    = '1')

LOGIN_ONE = dict(email    = USER_ONE['email'],
                 password = USER_ONE['password'])

LOGIN_TWO = dict(email    = USER_TWO['email'],
                 password = USER_TWO['password'])

plotNames = ['distance',
             'average_speed',
             'average_heartrate',
             'elapsed_time',
             'elevation_gain']


def make_and_login_user(client, db_instance, userDict, loginDict):
    global id_user
    rv = client.post('/create_user', data = userDict)
    rv = client.post(ROUTE_LOGIN, data = loginDict, follow_redirects = True)
    user = db_instance.session.query(User).filter(User.id == id_user).first()
    id_user += 1
    return user

def close_test():
    global id_run, id_user
    id_run  = 0
    id_user = 1

def add_run(db, name, strava_id, distance, start_date, elapsed_time, average_speed, average_heartrate, total_elevation_gain, user = None):
    global id_run
    r = Run(name                 = name,
            strava_id            = id_run,
            distance             = distance,
            start_date           = start_date,
            elapsed_time         = elapsed_time,
            average_speed        = average_speed,
            average_heartrate    = average_heartrate,
            total_elevation_gain = total_elevation_gain,
            runner_id            = user.id)
    id_run += 1
    db.session.add(r)
    db.session.commit()


def test_concatenate_run_name_id(client):
    run_names = []
    run_ids = []
    result = concatenate_run_name_id(run_names, run_ids)
    assert result == []

    run_names.append('val')
    result = concatenate_run_name_id(run_names, run_ids)
    assert result == []

    run_ids.append(1)
    result = concatenate_run_name_id(run_names, run_ids)
    assert result == [str(run_ids[0]) + '_' + run_names[0]]

    run_names.append('lol')
    run_ids.append(2)
    result = concatenate_run_name_id(run_names, run_ids)
    assert result == [str(run_ids[0]) + '_' + run_names[0],
                      str(run_ids[1]) + '_' + run_names[1]]

    close_test()

def test_statistics_base(client, celery_session_worker, db_instance):
    # No user
    rv = client.get(ROUTE_STATISTICS, follow_redirects=True)
    assert b'Anonymous' in rv.data

    # From now on all tests with User
    user = make_and_login_user(client, db_instance, USER_ONE, LOGIN_ONE)

    # No runs
    rv = client.get(ROUTE_STATISTICS, follow_redirects = True)
    assert rv.data.decode().count('<div class="items">') == 0

    # Run WITHOUT average_heartrate
    add_run(db_instance, 'test', 1, 10, dates['today'], 10, 10, None, 5, user)
    rv = client.get(ROUTE_STATISTICS, follow_redirects = True)
    assert rv.data.decode().count('<div class="items">') == 4

    # Run WITH average_heartrate
    add_run(db_instance, 'test', 1, 10, dates['today'], 10, 10, 10, 5, user)
    rv = client.get(ROUTE_STATISTICS, follow_redirects = True)
    assert rv.data.decode().count('<div class="items">') == 5

    client.get(ROUTE_LOGOUT, follow_redirects=True)

    close_test()


def path_file(filename, runner_id):
    return PLOTS_DIRECTORY + "/plots/" + filename + "_" + str(runner_id) + PLOTS_FORMAT


def test_statistics_two_users(client, celery_session_worker, db_instance):    
    userOne = make_and_login_user(client, db_instance, USER_ONE, LOGIN_ONE)
    print(userOne.id)
    add_run(db_instance, 'test', 1, 10, dates['today'], 10, 10, 10, 5, userOne)
    rv = client.get(ROUTE_STATISTICS, follow_redirects = True)
    assert rv.data.decode().count('<div class="items">') == 5
    
    for plotName in plotNames:
        path = path_file(plotName, userOne.id)
    assert os.path.exists(path) 

    client.get(ROUTE_LOGOUT, follow_redirects=True)


    userTwo = make_and_login_user(client, db_instance, USER_TWO, LOGIN_TWO)
    add_run(db_instance, 'test', 1, 10, dates['today'], 10, 10, 10, 5, userTwo)
    rv = client.get(ROUTE_STATISTICS, follow_redirects = True)
    assert rv.data.decode().count('<div class="items">') == 5

    for plotName in plotNames:
        path = path_file(plotName, userTwo.id)
    assert os.path.exists(path) 

    client.get(ROUTE_LOGOUT, follow_redirects=True)

    close_test()
    