from monolith.database import db, User, Run
from monolith.tests.utility import client, create_user, new_run, login
from monolith.tests.id_parser import get_element_by_id


def test_run(client):
    tested_app, app = client

    # prepare the database creating a new user
    reply = create_user(tested_app)  # creates a user with 'marco@prova.it' as email, default
    assert reply.status_code == 200

    # login as new user
    reply = login(tested_app, email='marco@prova.it', password='123456')
    assert reply.status_code == 200

    # retrieve the user object from db
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'marco@prova.it')
        user = q.first()

    # add the run
    with app.app_context():
        new_run(user)

    # retrieve the run
    with app.app_context():
        q = db.session.query(Run).filter(Run.id == 1)  # should be the first
        run = q.first()

    # retrieve run page
    reply = tested_app.get('/run/1')  # should be one, because the database is empty
    assert reply.status_code == 200

    # check the correctness of the fields
    assert get_element_by_id('start_date', str(reply.data)) == str(run.start_date)
    assert get_element_by_id('distance', str(reply.data)) == str(run.distance)
    assert get_element_by_id('elapsed_time', str(reply.data)) == str(run.elapsed_time // 60)
    assert get_element_by_id('average_speed', str(reply.data)) == str(run.average_speed)
    assert get_element_by_id('average_heartrate', str(reply.data)) == str(run.average_heartrate)
    assert get_element_by_id('total_elevation_gain', str(reply.data)) == str(run.total_elevation_gain)



