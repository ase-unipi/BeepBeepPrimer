import pytest
import os
from monolith.app import create_testing_app
from monolith.database import db


"""
    
    fixtures can be used from other funciton calling their name
    I'm not sure about their life span, but I'm sure that app, db_instance and client are recreated for each test
    so each test that use client has an empty database.

"""


# for now this is useless but why not keeping it...
@pytest.fixture(scope='session')
def use_celery_app_trap():
    return True


# I suppose is useless because they are the same of the real celery app but whatever
@pytest.fixture(scope='session')
def celery_config():

    return {
        'broker_url': 'redis://localhost:6379',
        'result_backend': 'redis://localhost:6379'
    }


# expose the app used for the test
@pytest.fixture
def app():
    _app = create_testing_app()
    yield _app
    os.unlink('monolith/beepbeeptest.db')


# expose the database of the app already usable with db.session
@pytest.fixture
def db_instance(app):
    db.init_app(app)
    db.create_all(app=app)
    with app.app_context():
        yield db


# overwrite the _APP in background to make it point to the test_app
# to use in every test that calls a function from the monolith/background.py file
# I want to remember that also /login make a calls to /fetch
# Thanks to Stefano we need to give background._APP the correct app to work with otherwise calls to
# fetch_all_runs would use the real app with the real db
@pytest.fixture
def background_app(app):
    from monolith import background
    background._APP = app
    yield app


# expose a client which is used to send requests to the app
@pytest.fixture
def client(app):
    client = app.test_client()

    yield client


"""
    Ok this is tricky.
    
    this function is called with a val argument and returns mocked_result_fun which is a function that can be called 
    with any number of arguments
    
    the function mocked_result_fun returns an Object which has a method get the get method returns the val parameter
    given to the initial function
    
    for usage example refers to test_core.py
    
    val must be a json object. See test_core.py for explanation
"""


def mocked_result(val):

    def mocked_result_fun(*args, **kwargs):
        value = val

        class MockResponse:
            def __init__(self, response=None):
                self.response = response

            def get(self, *args, **kwargs):
                return self.response

        return MockResponse(value)
    return mocked_result_fun


