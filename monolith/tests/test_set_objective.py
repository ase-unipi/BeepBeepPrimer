from monolith.tests.utility import client, login, new_user, new_objective
from monolith.database import db, User, Objective
from monolith.tests.id_parser import get_element_by_id


def test_set_objective(client):
    tested_app, app = client

    # test for create_objective having not logged in
    reply = tested_app.post('/create_objective')
    assert reply.status_code == 401
    
    # create a new user
    reply = new_user(tested_app)
    assert reply.status_code == 200 or reply.status_code == 302

    # USELESS ?
    # reply = login(tested_app, email='marco@prova.it', password='123456')
    # assert reply.status_code == 200

    # test for create_objective logged in
    reply = tested_app.post('/create_objective')
    assert reply.status_code == 200

    # retrieve the user object
    with app.app_context():
        q = db.session.query(User).filter(User.email == 'marco@prova.it')
        user = q.first()
        print('USER')
        print(user.id)
        print(user.email)
        print(user.firstname)
        print(user.lastname)
        print(user.password)
        print(user.strava_token)
        print(user.age)
        print(user.weight)
        print(user.max_hr)
        print(user.rest_hr)
        print(user.vo2max)
        print(user.is_active)
        print(user.is_admin)
        
    # add the objective
    with app.app_context():
        new_objective(user)
        
    # retrieve the objective page DOUBTS
    with app.app_context():
        q = db.session.query(Objective).filter(Objective.id == 1)
        objective = q.first()

    reply = tested_app.get('objectives')
    assert reply.status_code == 200
    
    assert get_element_by_id('name', str(reply.data)) == str(objective.name)
    assert get_element_by_id('start_date', str(reply.data)) == str(objective.start_date)
    assert get_element_by_id('end_date', str(reply.data)) == str(objective.end_date)
    assert get_element_by_id('target_distance', str(reply.data)) == str(objective.target_distance)
    assert get_element_by_id('runner', str(reply.data)) == str(objective.runner)

    
def test_get_objective_distance(client):
    pass
