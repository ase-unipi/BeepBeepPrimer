from unittest import mock
from monolith.database import User, Run
from tests.conftest import mocked_result




#test that no runs are returned if going simply to /runs
def test_empty_run(client):  # client is the yield variable in client function from conftest.py
    rv = client.get('/runs')

    #check if a 404 is indeed returned
    assert b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>404 Not Found</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.</p>\n' in rv.data;




# this is the interesting one test the /fetch with fake token and fake response
def test_single_functionalities_set(client, app, db_instance, celery_session_worker):
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
                             data=dict(submit='Publish', email='email', firstname='a', lastname='a', password='p',
                                       age='1',
                                       weight='1', max_hr='1', rest_hr='1', vo2max='1', ), follow_redirects=True)
        assert rv.data.decode('ascii').count('a a') == 1
        # create an user with emaill
        rv = client.post('/create_user',
                             data=dict(submit='Publish', email='emaill', firstname='a', lastname='a', password='p',
                                       age='1',
                                       weight='1', max_hr='1', rest_hr='1', vo2max='1', ), follow_redirects=True)

        rv = client.post('/login', data=dict(email='email', password='p'), follow_redirects=True)
        assert b'Hi email!' in rv.data
        assert b'Authorize Strava Access' in rv.data

        from monolith import background
        background._APP = app
        # Thanks to Stefano we need to give background._APP the correct app to work with otherwise calls to
        # fetch_all_runs would use the real app with the real db

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
            I've read the fucking source code of stravalib to see that client has this import ApiV3
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
            "id": 15450425037682, # changed id
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
            "id": 123456780, # changed id
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
        rv = client.post('/login', data=dict(email='emaill', password='p'), follow_redirects=True)
        with mock.patch('monolith.background.c.ApiV3', side_effect=fun):
            client.get('/strava_auth')
            r = db_instance.session.query(Run)
            assert r.count() == 4  # I should have 4 runs
            u = db_instance.session.query(User).filter(User.email == 'emaill').first()
            runs = db_instance.session.query(Run).filter(Run.runner == u )
            assert runs.count() == 2  # but only just 2 run for the user with email == emaill
            # nice so we created 2 user given then a fake token given them 2 fake runs each fetched 'directly'
            # from strava

            #daniele: login is fine, now let's see if we actualy manage to see our nice runs
            rv = client.get('/runs/3')

            #Check that header is correctly generated
            assert b'<html>\n  <head>\n    <link rel="stylesheet" href="/static/style.css">\n  </head>\n\n  <body>\n' in rv.data

            #run header properly generated
            assert b'<h1>Run</h1>' in rv.data

            #run name properly set
            assert b'<h3>Name: Happy Friday</h3>' in rv.data

            #distance properly set
            assert b'<td class="text-center">24931.4</td>' in rv.data

            #average speed properly set
            assert b'<td class="text-center">5.54</td>' in rv.data

            #duration properly set
            assert b'<td class="text-center">4500.0</td>' in rv.data

            #elevation gain properly set
            assert b'<td class="text-center">0.0</td>' in rv.data


            #and finally, check the whole page generation
            assert b'<html>\n  <head>\n    <link rel="stylesheet" href="/static/style.css">\n  </head>\n\n  <body>\n    \n    <h1>Run</h1>\n    <h3>Name: Happy Friday</h3>\n    <h3>Date: Wednesday 02/05/18 at 12:15</h3>\n    <table>\n      <thead>\n        <tr>\n           <th>Distance (m)</th>  <th>AVG Speed (m/s)</th>  <th>Elapsed Time (s)</th>  <th>Elevation (m)</th> \n          <th>Actions</th>\n        </tr>\n      </thead>\n      <tbody>\n        <tr>\n           <td class="text-center">24931.4</td>  <td class="text-center">5.54</td>  <td class="text-center">4500.0</td>  <td class="text-center">0.0</td> \n            <form action="/create_challenge" method="post">\n            <td>\n               <input type="hidden" name="id_run" value=3 />\n                <a href="#" onclick="document.forms[0].submit()"> \n                <img class="icon" src="/static/challenge.png"/> </a> </td> </form> \n        </tr>\n      </tbody>\n    </table>\n    \n  </body>\n</html>' in rv.data


# this is the interesting one test the /fetch with fake token and fake response
def test_full_page_generation(client, app, db_instance, celery_session_worker):
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
                         data=dict(submit='Publish', email='email', firstname='a', lastname='a', password='p',
                                   age='1',
                                   weight='1', max_hr='1', rest_hr='1', vo2max='1', ), follow_redirects=True)
        assert rv.data.decode('ascii').count('a a') == 1
        # create an user with emaill
        rv = client.post('/create_user',
                         data=dict(submit='Publish', email='emaill', firstname='a', lastname='a', password='p',
                                   age='1',
                                   weight='1', max_hr='1', rest_hr='1', vo2max='1', ), follow_redirects=True)

        rv = client.post('/login', data=dict(email='email', password='p'), follow_redirects=True)
        assert b'Hi email!' in rv.data
        assert b'Authorize Strava Access' in rv.data

        from monolith import background
        background._APP = app
        # Thanks to Stefano we need to give background._APP the correct app to work with otherwise calls to
        # fetch_all_runs would use the real app with the real db

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
            I've read the fucking source code of stravalib to see that client has this import ApiV3
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
        rv = client.post('/login', data=dict(email='emaill', password='p'), follow_redirects=True)
        with mock.patch('monolith.background.c.ApiV3', side_effect=fun):
            client.get('/strava_auth')
            r = db_instance.session.query(Run)
            assert r.count() == 4  # I should have 4 runs
            u = db_instance.session.query(User).filter(User.email == 'emaill').first()
            runs = db_instance.session.query(Run).filter(Run.runner == u)
            assert runs.count() == 2  # but only just 2 run for the user with email == emaill
            # nice so we created 2 user given then a fake token given them 2 fake runs each fetched 'directly'
            # from strava

            # daniele: login is fine, now let's see if we actualy manage to see our nice runs
            rv = client.get('/runs/3')

            #the whole page generation for run with ID = 3
            assert b'<html>\n  <head>\n    <link rel="stylesheet" href="/static/style.css">\n  </head>\n\n  <body>\n    \n    <h1>Run</h1>\n    <h3>Name: Happy Friday</h3>\n    <h3>Date: Wednesday 02/05/18 at 12:15</h3>\n    <table>\n      <thead>\n        <tr>\n           <th>Distance (m)</th>  <th>AVG Speed (m/s)</th>  <th>Elapsed Time (s)</th>  <th>Elevation (m)</th> \n          <th>Actions</th>\n        </tr>\n      </thead>\n      <tbody>\n        <tr>\n           <td class="text-center">24931.4</td>  <td class="text-center">5.54</td>  <td class="text-center">4500.0</td>  <td class="text-center">0.0</td> \n            <form action="/create_challenge" method="post">\n            <td>\n               <input type="hidden" name="id_run" value=3 />\n                <a href="#" onclick="document.forms[0].submit()"> \n                <img class="icon" src="/static/challenge.png"/> </a> </td> </form> \n        </tr>\n      </tbody>\n    </table>\n    \n  </body>\n</html>' in rv.data

            #the whole page generation for run with ID = 4
            rv2 = client.get('runs/4')
            print(rv2.data)

            assert b'<html>\n  <head>\n    <link rel="stylesheet" href="/static/style.css">\n  </head>\n\n  <body>\n    \n    <h1>Run</h1>\n    <h3>Name: Bondcliff</h3>\n    <h3>Date: Monday 30/04/18 at 12:35</h3>\n    <table>\n      <thead>\n        <tr>\n           <th>Distance (m)</th>  <th>AVG Speed (m/s)</th>  <th>Elapsed Time (s)</th>  <th>Elevation (m)</th> \n          <th>Actions</th>\n        </tr>\n      </thead>\n      <tbody>\n        <tr>\n           <td class="text-center">23676.5</td>  <td class="text-center">4.385</td>  <td class="text-center">5400.0</td>  <td class="text-center">0.0</td> \n            <form action="/create_challenge" method="post">\n            <td>\n               <input type="hidden" name="id_run" value=4 />\n                <a href="#" onclick="document.forms[0].submit()"> \n                <img class="icon" src="/static/challenge.png"/> </a> </td> </form> \n        </tr>\n      </tbody>\n    </table>\n    \n  </body>\n</html>' in rv2.data









