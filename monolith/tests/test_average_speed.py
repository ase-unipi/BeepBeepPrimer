from monolith.database import db, User, Run
from monolith.tests.utility import client, create_user, new_user, login, new_run
from monolith.tests.id_parser import get_element_by_id


def test_average_speed(client):
    tested_app, app = client

    # prepare the database creating a new user
    reply = create_user(tested_app)  # creates a user with 'marco@prova.it' as email, default
    assert reply.status_code == 200

    # login as new user
    reply = login(tested_app, email='marco@prova.it', password='123456')
    assert reply.status_code == 200

    # retrieve the user object and login
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'marco@prova.it')
        user = q.first()
        user.strava_token = "fake_token"
        db.session.commit()

    # The average speed should be 0 if there are no runs
    reply = tested_app.get('/')
    assert reply.status_code == 200
    assert get_element_by_id('total_average_speed', str(reply.data)) == str(0)

    # add a run
    with app.app_context():
        new_run(user)

    # retrieve the run
    with app.app_context():
        q = db.session.query(Run).filter(Run.id == 1)  # should be the first
        run1 = q.first()

    # with only a run the average speed should be the average speed of the run
    reply = tested_app.get('/')
    assert reply.status_code == 200
    assert get_element_by_id('total_average_speed', str(reply.data)) == str(round(run1.average_speed, 2))

    # add another run
    with app.app_context():
        new_run(user)

    # retrieve the runs list
    with app.app_context():
        runs = db.session.query(Run).filter()  # should be all owned by our user

    # with multiples runs the average speed should be the average of the average speed of each run
    total_average_speed = 0
    for run in runs:
        total_average_speed += run.average_speed
    total_average_speed /= runs.count()

    reply = tested_app.get('/')
    assert reply.status_code == 200
    assert get_element_by_id('total_average_speed', str(reply.data)) == str(round(total_average_speed, 2))
