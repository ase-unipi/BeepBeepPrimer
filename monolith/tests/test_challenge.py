from monolith.tests.utility import client, login
from monolith.database import db, User, Report
from monolith.tests.utility import create_user,new_predefined_run, new_predefined_run_equal, new_predefined_run_test

def test_create_repo(client):
    tested_app, app = client

    user = create_user(tested_app,email='mcriucc@gmail.com', firstname='mariacristina', lastname='uccheddu', password='ciao',
                                              age=23,
                                              weight=70,
                                              max_hr=120,
                                              rest_hr=60,
                                              vo2max=99)

    assert login(tested_app, 'mcriucc@gmail.com', 'ciao').status_code == 200

    run_one = new_predefined_run_equal(user)
    run_two = new_predefined_run(user)
    run_three = new_predefined_run_test(user)

    reply = tested_app.post('/challenge', data=dict(
        start_date="asd",
        name="Wrong test1"
    ))