from monolith.tests.utility import client, login, new_user, new_run, new_objective
from monolith.database import db, User, Objective
from datetime import datetime, timedelta
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
        
    # add the objective
    with app.app_context():
        new_objective(user)
        
    # retrieve the objective page DOUBTS
    with app.app_context():
        objective = db.session.query(Objective).filter(Objective.id == 1).first()

    reply = tested_app.get('objectives')
    assert reply.status_code == 200
    
    assert get_element_by_id('name', str(reply.data)) == str(objective.name)
    assert get_element_by_id('start_date', str(reply.data)) == str(objective.start_date)
    assert get_element_by_id('end_date', str(reply.data)) == str(objective.end_date)
    assert get_element_by_id('target_distance', str(reply.data)) == str(objective.target_distance)
    assert get_element_by_id('runner_id', str(reply.data)) == str(objective.runner_id)

def test_check_objective(client):
    tested_app, app = client

    # create a new user
    reply = new_user(tested_app)
    assert reply.status_code == 302

    # login as new user
    reply = login(tested_app, email='marco@prova.it', password='123456')
    assert reply.status_code == 200

    # retrieve the user object and login
    user = None
    with app.app_context():
        user = db.session.query(User).filter(User.email == 'marco@prova.it').first()

    # create some test runs
    run_1 = new_run(user, distance = 20, elapsed_time = 1024, start_date = datetime.now())
    run_2 = new_run(user, distance = 10, elapsed_time = 660, start_date = datetime.now() + timedelta(day = 2))
    run_3 = new_run(user, distance = 30, elapsed_time = 2048, start_date = datetime.now() + timedelta(day = 4))

    runs = [run_1, run_2, run_3]

    # check an objective with completion = 0%
    objective_1 = new_objective(user, start_date = datetime.now(), end_date = datetime.now() + timedelta(days = 7), target_distance = 3000)
    assert objective_1.completion(runs) == 0

    # check an objective with completion 50%
    objective_2 = new_objective(user, start_date = datetime.now(), end_date = datetime.now() + timedelta(days = 1), target_distance = 2048)
    assert objective_2.completion(runs) == 0.5

    # check an objective with completion of 100%
    objective_3 = new_objective(user, start_date = datetime.now(), end_date = datetime.now() + timedelta(days = 1), target_distance = 20)
    assert objective_3.completion(runs) == 1

    # check an objective with completion of 100% with exactly the km needed to complete it
    objective_4 = new_objective(user, start_date = datetime.now(), end_date = datetime.now() + timedelta(days = 1), target_distance = 1024)
    assert objective_4.completion(runs) == 1
    




    
