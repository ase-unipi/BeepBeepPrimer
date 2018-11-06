from monolith.tests.utility import client, login, new_user
from monolith.database import db, User, Objective


def test_set_objective(client):
    tested_app, app = client

    # create a new user
    reply = new_user(tested_app)
    assert reply.status_code == 200
    
    # test for create_obective not logged in
    reply = tested_app.post('/create_objective')
    assert reply.status_code == 401

    reply = login(tested_app, email='marco@prova.it', password='123456')
    assert reply.status_code == 200

    
