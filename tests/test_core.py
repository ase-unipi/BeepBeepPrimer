from unittest import mock
from monolith.database import User, Run
from tests.conftest import mocked_result
from datetime import date


# Test that the index shows the correct page when not authenticated
def test_index(client):  # client is the yield variable in client function from conftest.py
    rv = client.get('/')  # send a get request for '/'
    assert b'<h1 class="textPumpkingDark text-center"> Hi Anonymous</h1>' in rv.data
    assert b'<h3 class="textJeansDark text-center"> Please Login or Register </h3>' in rv.data
    # b'' converts the string in binary


def test_list_of_runs(client, db_instance, background_app, celery_session_worker):
    rv = client.post('/create_user', data=dict(submit='Publish', email='email@email.com', firstname='a', lastname='a',
                                               password='p', age='1',
                                               weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                     follow_redirects=True)
    assert b'Hi Anonymous' in rv.data
    assert db_instance.session.query(User).count() == 1
    client.post('/login', data=dict(email='email@email.com', password='p'), follow_redirects=True)
    with mock.patch('monolith.views.auth.Client') as mocked:
        mocked.return_value.exchange_code_for_token.return_value = "blablabla"
        fun = mocked_result([])
        with mock.patch('monolith.background.c.ApiV3', side_effect=fun):
            client.get('/strava_auth')
    r = Run(name='run', strava_id=1, distance=2000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=20.121, average_heartrate=0, runner_id=1)
    db_instance.session.add(r)
    db_instance.session.commit()
    r = Run(name='run', strava_id=2, distance=2000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=3.211, average_heartrate=0, runner_id=1)
    db_instance.session.add(r)
    db_instance.session.commit()
    r = Run(name='run', strava_id=3, distance=3000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=17.19, average_heartrate=0, runner_id=1)
    db_instance.session.add(r)
    db_instance.session.commit()
    rv = client.get('/')
    print(repr(rv.data.decode('ascii')))
    assert b' <tr>\n            <td> run </td>\n            <td class="text-center">\n             ' \
           b' <a href="/runs/1"">\n                <img class="icon" src="/static/view.png"/>\n             ' \
           b' </a>\n            </td>\n            <form action="/create_challenge" method="post">\n             ' \
           b' <input type="hidden" name="id_run" value=1 />\n              <td class="text-center">\n              ' \
           b'  <a href="#" onclick="document.forms[1-1].submit()">\n                 ' \
           b' <img class="icon" src="/static/challenge.png"/>\n                </a>\n              </td>\n          ' \
           b'  </form> \n          </tr>\n' in rv.data
    assert b' <tr>\n            <td> run </td>\n            <td class="text-center">\n             ' \
           b' <a href="/runs/2"">\n                <img class="icon" src="/static/view.png"/>\n             ' \
           b' </a>\n            </td>\n            <form action="/create_challenge" method="post">\n             ' \
           b' <input type="hidden" name="id_run" value=2 />\n              <td class="text-center">\n              ' \
           b'  <a href="#" onclick="document.forms[2-1].submit()">\n                 ' \
           b' <img class="icon" src="/static/challenge.png"/>\n                </a>\n              </td>\n          ' \
           b'  </form> \n          </tr>\n' in rv.data
    assert b' <tr>\n            <td> run </td>\n            <td class="text-center">\n             ' \
           b' <a href="/runs/3"">\n                <img class="icon" src="/static/view.png"/>\n             ' \
           b' </a>\n            </td>\n            <form action="/create_challenge" method="post">\n             ' \
           b' <input type="hidden" name="id_run" value=3 />\n              <td class="text-center">\n              ' \
           b'  <a href="#" onclick="document.forms[3-1].submit()">\n                 ' \
           b' <img class="icon" src="/static/challenge.png"/>\n                </a>\n              </td>\n          ' \
           b'  </form> \n          </tr>\n' in rv.data


def test_list_of_run_more_users(client, db_instance, background_app, celery_session_worker):
    rv = client.post('/create_user', data=dict(submit='Publish', email='email@email.com', firstname='a', lastname='a',
                                               password='p', age='1',
                                               weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                     follow_redirects=True)
    assert b'Hi Anonymous' in rv.data
    assert db_instance.session.query(User).count() == 1
    client.post('/create_user', data=dict(submit='Publish', email='emaill@email.com', firstname='a', lastname='a',
                                          password='p', age='1',
                                          weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                follow_redirects=True)
    assert b'Hi Anonymous' in rv.data
    assert db_instance.session.query(User).count() == 2
    client.post('/login', data=dict(email='emaill@email.com', password='p'), follow_redirects=True)
    with mock.patch('monolith.views.auth.Client') as mocked:
        mocked.return_value.exchange_code_for_token.return_value = "blablabla"
        fun = mocked_result([])
        with mock.patch('monolith.background.c.ApiV3', side_effect=fun):
            client.get('/strava_auth')
    r = Run(name='run', strava_id=1, distance=2000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=20.121, average_heartrate=0, runner_id=1)
    db_instance.session.add(r)
    db_instance.session.commit()
    r = Run(name='run', strava_id=2, distance=2000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=3.211, average_heartrate=0, runner_id=2)
    db_instance.session.add(r)
    db_instance.session.commit()
    r = Run(name='run', strava_id=3, distance=3000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=17.19, average_heartrate=0, runner_id=2)
    db_instance.session.add(r)
    db_instance.session.commit()
    rv = client.get('/')
    print(repr(rv.data.decode('ascii')))
    assert b' <tr>\n            <td> run </td>\n            <td class="text-center">\n             ' \
           b' <a href="/runs/2"">\n                <img class="icon" src="/static/view.png"/>\n             ' \
           b' </a>\n            </td>\n            <form action="/create_challenge" method="post">\n             ' \
           b' <input type="hidden" name="id_run" value=2 />\n              <td class="text-center">\n              ' \
           b'  <a href="#" onclick="document.forms[1-1].submit()">\n                 ' \
           b' <img class="icon" src="/static/challenge.png"/>\n                </a>\n              </td>\n          ' \
           b'  </form> \n          </tr>\n' in rv.data
    assert b' <tr>\n            <td> run </td>\n            <td class="text-center">\n             ' \
           b' <a href="/runs/3"">\n                <img class="icon" src="/static/view.png"/>\n             ' \
           b' </a>\n            </td>\n            <form action="/create_challenge" method="post">\n             ' \
           b' <input type="hidden" name="id_run" value=3 />\n              <td class="text-center">\n              ' \
           b'  <a href="#" onclick="document.forms[2-1].submit()">\n                 ' \
           b' <img class="icon" src="/static/challenge.png"/>\n                </a>\n              </td>\n          ' \
           b'  </form> \n          </tr>\n' in rv.data


def test_average_speed_single_run(client, db_instance, background_app, celery_session_worker):
    rv = client.post('/create_user', data=dict(submit='Publish', email='email@email.com', firstname='a', lastname='a',
                                               password='p', age='1',
                                               weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                     follow_redirects=True)
    assert b'Hi Anonymous' in rv.data
    assert db_instance.session.query(User).count() == 1
    client.post('/login', data=dict(email='email@email.com', password='p'), follow_redirects=True)
    with mock.patch('monolith.views.auth.Client') as mocked:
        mocked.return_value.exchange_code_for_token.return_value = "blablabla"
        fun = mocked_result([])
        with mock.patch('monolith.background.c.ApiV3', side_effect=fun):
            client.get('/strava_auth')
    r = Run(name='run', strava_id=1, distance=2000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=20.12, average_heartrate=0, runner_id=1)
    db_instance.session.add(r)
    db_instance.session.commit()
    rv = client.get("/")
    assert b'20.12 m/s' in rv.data


def test_average_speed_two_runs(client, db_instance, background_app, celery_session_worker):
    rv = client.post('/create_user', data=dict(submit='Publish', email='email@email.com', firstname='a', lastname='a',
                                               password='p', age='1',
                                               weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                     follow_redirects=True)
    assert b'Hi Anonymous' in rv.data
    assert db_instance.session.query(User).count() == 1
    client.post('/login', data=dict(email='email@email.com', password='p'), follow_redirects=True)
    with mock.patch('monolith.views.auth.Client') as mocked:
        mocked.return_value.exchange_code_for_token.return_value = "blablabla"
        fun = mocked_result([])
        with mock.patch('monolith.background.c.ApiV3', side_effect=fun):
            client.get('/strava_auth')
    r = Run(name='run', strava_id=1, distance=2000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=20.12, average_heartrate=0, runner_id=1)
    db_instance.session.add(r)
    db_instance.session.commit()
    r = Run(name='run', strava_id=2, distance=3000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=17.19, average_heartrate=0, runner_id=1)
    db_instance.session.add(r)
    db_instance.session.commit()
    rv = client.get("/")
    print(rv.data.decode('ascii'))
    assert b'18.66 m/s' in rv.data


def test_average_speed_periodic(client, db_instance, background_app, celery_session_worker):
    rv = client.post('/create_user', data=dict(submit='Publish', email='email@email.com', firstname='a', lastname='a',
                                               password='p', age='1',
                                               weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                     follow_redirects=True)
    assert b'Hi Anonymous' in rv.data
    assert db_instance.session.query(User).count() == 1
    rv = client.post('/login', data=dict(email='email@email.com', password='p'), follow_redirects=True)
    with mock.patch('monolith.views.auth.Client') as mocked:
        mocked.return_value.exchange_code_for_token.return_value = "blablabla"
        fun = mocked_result([])
        with mock.patch('monolith.background.c.ApiV3', side_effect=fun):
            client.get('/strava_auth')
    r = Run(name='run', strava_id=1, distance=2000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=20.12, average_heartrate=0, runner_id=1)
    db_instance.session.add(r)
    db_instance.session.commit()
    r = Run(name='run', strava_id=2, distance=3000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=17.19, average_heartrate=0, runner_id=1)
    db_instance.session.add(r)
    db_instance.session.commit()
    r = Run(name='run', strava_id=3, distance=3000, start_date=date.today(), elapsed_time=1000 * 50,
            average_speed=2.13, average_heartrate=0, runner_id=1)
    db_instance.session.add(r)
    db_instance.session.commit()
    rv = client.get("/")
    print(rv.data.decode('ascii'))
    assert b'13.15 m/s' in rv.data


# Test that checks if the create_user page permits to create 2 user with the same email
def test_create_same_user(client, db_instance):
    rv = client.post('/create_user', data=dict(submit='Publish', email='email@email.com', firstname='a', lastname='a',
                                               password='p', age='1',
                                               weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                     follow_redirects=True)
    # follow_redirects parameter to follow the enormous number of redirect that we have
    # data=dict to pass data as a form, different syntax to pass json or others
    assert b'Hi Anonymous' in rv.data
    assert db_instance.session.query(User).count() == 1
    rv = client.post('/create_user',
                     data=dict(email='email@email.com', firstname='a', lastname='a', password='p', age='1',
                               weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                     follow_redirects=True)
    assert b'This email has already been used' in rv.data
    assert db_instance.session.query(User).count() == 1


def test_create_bad_email_user(client, db_instance):
    rv = client.post('/create_user', data=dict(submit='Publish', email='emailemail.com', firstname='a', lastname='a',
                                               password='p', age='1',
                                               weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                     follow_redirects=True)

    assert b'Invalid email address.' in rv.data
    r = db_instance.session.query(User)
    assert r.count() == 0

    rv = client.post('/create_user', data=dict(submit='Publish', email='@email.com', firstname='a', lastname='a',
                                               password='p', age='1',
                                               weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                     follow_redirects=True)

    assert b'Invalid email address.' in rv.data
    r = db_instance.session.query(User)
    assert r.count() == 0

    rv = client.post('/create_user', data=dict(submit='Publish', email='email@', firstname='a', lastname='a',
                                               password='p', age='1',
                                               weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                     follow_redirects=True)

    assert b'Invalid email address.' in rv.data
    r = db_instance.session.query(User)
    assert r.count() == 0

    rv = client.post('/create_user', data=dict(submit='Publish', email='email@emailcom', firstname='a', lastname='a',
                                               password='p', age='1',
                                               weight='1', max_hr='1', rest_hr='1', vo2max='1'),
                     follow_redirects=True)

    assert b'Invalid email address.' in rv.data
    r = db_instance.session.query(User)
    assert r.count() == 0


# test the login and logout features now the login make a call to celery so we need celery_session_worker
# tested with only celery_worker but got stuck after the execution of this function
def test_login_logout(client, background_app, celery_session_worker, db_instance):
    rv = client.post('/create_user',
                     data=dict(submit='Publish', email='email@email.com', firstname='a', lastname='a', password='p',
                               age='1',
                               weight='1', max_hr='1', rest_hr='1', vo2max='1', ), follow_redirects=True)
    assert b'Hi Anonymous' in rv.data
    assert db_instance.session.query(User).count() == 1

    rv = client.post('/login', data=dict(email='email@email.com', password='b'), follow_redirects=True)

    assert b'password' in rv.data

    rv = client.post('/login', data=dict(email='email@email.com', password='p'), follow_redirects=True)


    assert b'Hi email@email.com' in rv.data
    assert b'Authorize Strava Access' in rv.data

    rv = client.get('/logout', follow_redirects=True)

    assert b'Hi Anonymous' in rv.data


def test_login_delete(client, db_instance, background_app, celery_session_worker):
    rv = client.post('/create_user',
                     data=dict(submit='Publish', email='email@email.com', firstname='a', lastname='a', password='p',
                               age='1',
                               weight='1', max_hr='1', rest_hr='1', vo2max='1', ), follow_redirects=True)
    assert b'Hi Anonymous' in rv.data
    assert db_instance.session.query(User).count() == 1

    rv = client.post('/login', data=dict(email='email@email.com', password='p'), follow_redirects=True)


    assert b'Hi email@email.com' in rv.data
    assert b'Authorize Strava Access' in rv.data

    rv = client.get('/remove_user')
    assert b'<h2 class="formTitle">Delete Profile</h2>\n\n    <fieldset>\n      \n       ' \
           b' <label class="labelFor" for="password"><label for="password">Password</label></label>\n       ' \
           b' <input id="password" name="password" required type="password" value="">\n        \n      \n\n    ' \
           b'</fieldset>\n    <button class="button buttonPumpkinDark" type="submit">Delete Profile</button>' in rv.data
    assert db_instance.session.query(User).count() == 1
    rv = client.post('/remove_user', data=dict(submit='Publish'), follow_redirects=True)
    print(repr(rv.data.decode('ascii')))
    assert b'<h2 class="formTitle">Delete Profile</h2>\n\n    <fieldset>\n      \n        ' \
           b'<label class="labelFor" for="password"><label for="password">Password</label></label>\n        ' \
           b'<input id="password" name="password" required type="password" value="">\n        \n          \n         ' \
           b'   <p class="help-block">This field is required.</p>\n          \n        \n      \n\n    </fieldset>\n' \
           b'    <button class="button buttonPumpkinDark" type="submit">Delete Profile</button>' in rv.data
    assert db_instance.session.query(User).count() == 1
    rv = client.post('/remove_user', data=dict(submit='Publish', password='b'), follow_redirects=True)
    assert b'<h2 class="formTitle">Delete Profile</h2>\n\n    <fieldset>\n      \n       ' \
           b' <label class="labelFor" for="password"><label for="password">Password</label></label>\n       ' \
           b' <input id="password" name="password" required type="password" value="">\n        \n      \n\n    ' \
           b'</fieldset>\n    <button class="button buttonPumpkinDark" type="submit">Delete Profile</button>' in rv.data
    assert db_instance.session.query(User).count() == 1
    rv = client.post('/remove_user', data=dict(submit='Publish', password='p'), follow_redirects=True)
    assert b'Hi Anonymous' in rv.data


def test_fetch_with_no_valid_token(client, db_instance, background_app, celery_session_worker):
    rv = client.post('/create_user',
                     data=dict(submit='Publish', email='email@email.com', firstname='a', lastname='a', password='p',
                               age='1',
                               weight='1', max_hr='1', rest_hr='1', vo2max='1', ), follow_redirects=True)
    assert b'Hi Anonymous' in rv.data
    assert db_instance.session.query(User).count() == 1

    rv = client.post('/login', data=dict(email='email@email.com', password='p'), follow_redirects=True)

    
    assert b'Hi email@email.com' in rv.data
    assert b'Authorize Strava Access' in rv.data
    with mock.patch('monolith.views.auth.Client') as mocked:
        mocked.return_value.exchange_code_for_token.return_value = "blablabla"

        fun = mocked_result([])
        with mock.patch('monolith.background.c.ApiV3', side_effect=fun):
            client.get('/strava_auth')

        r = db_instance.session.query(User)  # use the db_instance as in a normal not testing file (thx me later)
        u = r.first()
        assert u.strava_token == "blablabla"

    client.get('/fetch')
    assert db_instance.session.query(User).first().strava_token is None


def test_login_delete_strava(client, db_instance, background_app, celery_session_worker):
    rv = client.post('/create_user',
                     data=dict(submit='Publish', email='email@email.com', firstname='a', lastname='a', password='p',
                               age='1',
                               weight='1', max_hr='1', rest_hr='1', vo2max='1', ), follow_redirects=True)
    assert b'Hi Anonymous' in rv.data
    assert db_instance.session.query(User).count() == 1

    rv = client.post('/login', data=dict(email='email@email.com', password='p'), follow_redirects=True)

    assert b'Hi email@email.com' in rv.data
    assert b'Authorize Strava Access' in rv.data
    with mock.patch('monolith.views.auth.Client') as mocked:
        mocked.return_value.exchange_code_for_token.return_value = "blablabla"

        fun = mocked_result([])
        with mock.patch('monolith.background.c.ApiV3', side_effect=fun):
            client.get('/strava_auth')
        with mock.patch('monolith.views.auth.Client') as mocked:
            client.post('/remove_user', data=dict(submit='Publish', password='p'), follow_redirects=True)
            assert mocked.return_value.deauthorize.called


# this is the interesting one test the /fetch with fake token and fake response
def test_create_runs(client, background_app, db_instance, celery_session_worker):
    """

    we use client app and db_instance celery_worker creates a celery worker instance for this test so we don't need to
    have the celery program running (we still need redis-server I din't figured out how to start it from here

    :param client:
    :param app:
    :param db_instance:
    :param celery_worker:
    :return:
    """

    # mock.patch create an object that will be used instead of the one inside brackets
    # monolith.views.auth.Client is stravalib.Client but we need to mock the one in the
    # right context
    with mock.patch('monolith.views.auth.Client') as mocked:
        # mocked.return_value is what is returned when we call Client() so line 17 of views.auth.py
        # mocked.return_value.exchange_code_for_token.return_value is what is returned when we call
        # client().exchange_code_for_token(args...) so line 18 and 19 of views.auth.py
        mocked.return_value.exchange_code_for_token.return_value = "blablabla"
        # create an user with email
        rv = client.post('/create_user',
                         data=dict(submit='Publish', email='email@email.com', firstname='a', lastname='a', password='p',
                                   age='1',
                                   weight='1', max_hr='1', rest_hr='1', vo2max='1', ), follow_redirects=True)
        assert b'Hi Anonymous' in rv.data
        assert db_instance.session.query(User).count() == 1
        # create an user with emaill
        rv = client.post('/create_user',
                         data=dict(submit='Publish', email='emaill@email.com', firstname='a', lastname='a',
                                   password='p',
                                   age='1',
                                   weight='1', max_hr='1', rest_hr='1', vo2max='1', ), follow_redirects=True)

        rv = client.post('/login', data=dict(email='email@email.com', password='p'), follow_redirects=True)

        assert b'Hi email@email.com' in rv.data
        assert b'Authorize Strava Access' in rv.data

        """
            Alright calling mocked_result from conftest.py
            with what looks like the response we would get if we call client.get_activities...
            result copied from strava api references
        """
        fun = mocked_result([{
            "resource_state": 2,
            "athlete": {
                "id": 134815,
                "resource_state": 1
            },
            "name": "Happy Friday",
            "distance": 24931.4,
            "moving_time": 4500,
            "elapsed_time": 4500,
            "total_elevation_gain": 0,
            "type": "Run",
            "workout_type": None,
            "id": 154504250376823,
            "external_id": "garmin_push_12345678987654321",
            "upload_id": 987654321234567891234,
            "start_date": "2018-05-02T12:15:09Z",
            "start_date_local": "2018-05-02T05:15:09Z",
            "timezone": "(GMT-08:00) America/Los_Angeles",
            "utc_offset": -25200,
            "start_latlng": None,
            "end_latlng": None,
            "location_city": None,
            "location_state": None,
            "location_country": "United States",
            "start_latitude": None,
            "start_longitude": None,
            "achievement_count": 0,
            "kudos_count": 3,
            "comment_count": 1,
            "athlete_count": 1,
            "photo_count": 0,
            "map": {
                "id": "a12345678987654321",
                "summary_polyline": None,
                "resource_state": 2
            },
            "trainer": True,
            "commute": False,
            "manual": False,
            "private": False,
            "flagged": False,
            "gear_id": "b12345678987654321",
            "from_accepted_tag": False,
            "average_speed": 5.54,
            "max_speed": 11,
            "average_cadence": 67.1,
            "average_watts": 175.3,
            "weighted_average_watts": 210,
            "kilojoules": 788.7,
            "device_watts": True,
            "has_heartrate": True,
            "average_heartrate": 140.3,
            "max_heartrate": 178,
            "max_watts": 406,
            "pr_count": 0,
            "total_photo_count": 1,
            "has_kudoed": False,
            "suffer_score": 82
        }, {
            "resource_state": 2,
            "athlete": {
                "id": 167560,
                "resource_state": 1
            },
            "name": "Bondcliff",
            "distance": 23676.5,
            "moving_time": 5400,
            "elapsed_time": 5400,
            "total_elevation_gain": 0,
            "type": "Run",
            "workout_type": None,
            "id": 1234567809,
            "external_id": "garmin_push_12345678987654321",
            "upload_id": 1234567819,
            "start_date": "2018-04-30T12:35:51Z",
            "start_date_local": "2018-04-30T05:35:51Z",
            "timezone": "(GMT-08:00) America/Los_Angeles",
            "utc_offset": -25200,
            "start_latlng": None,
            "end_latlng": None,
            "location_city": None,
            "location_state": None,
            "location_country": "United States",
            "start_latitude": None,
            "start_longitude": None,
            "achievement_count": 0,
            "kudos_count": 4,
            "comment_count": 0,
            "athlete_count": 1,
            "photo_count": 0,
            "map": {
                "id": "a12345689",
                "summary_polyline": None,
                "resource_state": 2
            },
            "trainer": True,
            "commute": False,
            "manual": False,
            "private": False,
            "flagged": False,
            "gear_id": "b12345678912343",
            "from_accepted_tag": False,
            "average_speed": 4.385,
            "max_speed": 8.8,
            "average_cadence": 69.8,
            "average_watts": 200,
            "weighted_average_watts": 214,
            "kilojoules": 1080,
            "device_watts": True,
            "has_heartrate": True,
            "average_heartrate": 152.4,
            "max_heartrate": 183,
            "max_watts": 403,
            "pr_count": 0,
            "total_photo_count": 1,
            "has_kudoed": False,
            "suffer_score": 162
        }])

        """
            I've read the fudging source code of stravalib to see that client has this import ApiV3
            and that when we call get_activities will be called ApiV3 get method...

            So now we are mocking ApiV3 with fun which is the result from mocked_result
            fun is a function which when called returns an object with a get method...
            so when i call client.get('/fetch')
            a call to fetch_all_runs will be made which creates an object of type
            stravalib.Client which creates inside of him an object ApiV3 which is a moked
            object with just the get method.

            I've lost my mind yesterday to figure it out,
            ApiV3.get is masked from visibility rules so we need to mask it directly furthermore
            get_activities returns an iterator over an object of the stravalib library
            instead ApiV3.get returns a json!!!!!!!!!!!!!
            So... the arguments passed to mocked_result must be a json object
        """
        with mock.patch('monolith.background.c.ApiV3', side_effect=fun):
            client.get('/strava_auth')
            # calling strava_auth with the mocked instance of stravalib.client which set the token then make a call to
            # fetch_runs_for_user
            r = db_instance.session.query(User)  # use the db_instance as in a normal not testing file (thx me later)
            u = r.first()
            assert u.strava_token == 'blablabla'  # this assert prove the usage of the mocked client
            rv = client.get('/fetch')
        # I logout from the this user
        rv = client.get('/logout', follow_redirects=True)

        # create another mocked result with two activities with different id from the previous one
        fun = mocked_result([{
            "resource_state": 2,
            "athlete": {
                "id": 13481,
                "resource_state": 1
            },
            "name": "Happy Friday",
            "distance": 24931.4,
            "moving_time": 4500,
            "elapsed_time": 4500,
            "total_elevation_gain": 0,
            "type": "Run",
            "workout_type": None,
            "id": 15450425037682,  # changed id
            "external_id": "garmin_push_12345678987654321",
            "upload_id": 987654321234567891234,
            "start_date": "2018-05-02T12:15:09Z",
            "start_date_local": "2018-05-02T05:15:09Z",
            "timezone": "(GMT-08:00) America/Los_Angeles",
            "utc_offset": -25200,
            "start_latlng": None,
            "end_latlng": None,
            "location_city": None,
            "location_state": None,
            "location_country": "United States",
            "start_latitude": None,
            "start_longitude": None,
            "achievement_count": 0,
            "kudos_count": 3,
            "comment_count": 1,
            "athlete_count": 1,
            "photo_count": 0,
            "map": {
                "id": "a12345678987654321",
                "summary_polyline": None,
                "resource_state": 2
            },
            "trainer": True,
            "commute": False,
            "manual": False,
            "private": False,
            "flagged": False,
            "gear_id": "b12345678987654321",
            "from_accepted_tag": False,
            "average_speed": 5.54,
            "max_speed": 11,
            "average_cadence": 67.1,
            "average_watts": 175.3,
            "weighted_average_watts": 210,
            "kilojoules": 788.7,
            "device_watts": True,
            "has_heartrate": True,
            "average_heartrate": 140.3,
            "max_heartrate": 178,
            "max_watts": 406,
            "pr_count": 0,
            "total_photo_count": 1,
            "has_kudoed": False,
            "suffer_score": 82
        }, {
            "resource_state": 2,
            "athlete": {
                "id": 16756,
                "resource_state": 1
            },
            "name": "Bondcliff",
            "distance": 23676.5,
            "moving_time": 5400,
            "elapsed_time": 5400,
            "total_elevation_gain": 0,
            "type": "Run",
            "workout_type": None,
            "id": 123456780,  # changed id
            "external_id": "garmin_push_12345678987654321",
            "upload_id": 1234567819,
            "start_date": "2018-04-30T12:35:51Z",
            "start_date_local": "2018-04-30T05:35:51Z",
            "timezone": "(GMT-08:00) America/Los_Angeles",
            "utc_offset": -25200,
            "start_latlng": None,
            "end_latlng": None,
            "location_city": None,
            "location_state": None,
            "location_country": "United States",
            "start_latitude": None,
            "start_longitude": None,
            "achievement_count": 0,
            "kudos_count": 4,
            "comment_count": 0,
            "athlete_count": 1,
            "photo_count": 0,
            "map": {
                "id": "a12345689",
                "summary_polyline": None,
                "resource_state": 2
            },
            "trainer": True,
            "commute": False,
            "manual": False,
            "private": False,
            "flagged": False,
            "gear_id": "b12345678912343",
            "from_accepted_tag": False,
            "average_speed": 4.385,
            "max_speed": 8.8,
            "average_cadence": 69.8,
            "average_watts": 200,
            "weighted_average_watts": 214,
            "kilojoules": 1080,
            "device_watts": True,
            "has_heartrate": True,
            "average_heartrate": 152.4,
            "max_heartrate": 183,
            "max_watts": 403,
            "pr_count": 0,
            "total_photo_count": 1,
            "has_kudoed": False,
            "suffer_score": 162
        }])
        # log in with the other user
        rv = client.post('/login', data=dict(email='emaill@email.com', password='p'), follow_redirects=True)
        with mock.patch('monolith.background.c.ApiV3', side_effect=fun):
            client.get('/strava_auth')
            r = db_instance.session.query(Run)
            assert r.count() == 4  # I should have 4 runs
            u = db_instance.session.query(User).filter(User.email == 'emaill@email.com').first()
            r = db_instance.session.query(Run).filter(Run.runner == u)
            assert r.count() == 2  # but only just 2 run for the user with email == emaill
            # nice so we created 2 user given then a fake token given them 2 fake runs each fetched 'directly'
            # from strava
