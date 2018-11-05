from monolith.tests.utility import client, login, new_user
from monolith.database import db, User

def test_set_objective(client):
    tested_app, app = client
    
    reply = new_user(tested
    assert = reply.status_

    # doing a GET create_objective returns the template 
    # create objective  without having logged in 
    reply = tested_app.get('/create_objective')
    assert reply.status_code == 401

    
