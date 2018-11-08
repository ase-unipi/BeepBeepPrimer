from monolith.tests.utility import client, login, create_user, logout
from monolith.database import db, User

# def new_user(client, email='marco@prova.it', firstname='marco', lastname='mario', password='123456', age=18,
#              weight=70, max_hr=120, rest_hr=65, vo2max=99):

#     return client.post('/create_user', data=dict(email=email,
#                                                  firstname=firstname,
#                                                  lastname=lastname,
#                                                  password=password,
#                                                  age=age,
#                                                  weight=weight,
#                                                  max_hr=max_hr,
#                                                  rest_hr=rest_hr,
#                                                  vo2max=vo2max))
                                                 #, follow_redirects=True)

def test_delete(client):
    tested_app, app = client

    reply = create_user(tested_app)  # creates a user with 'marco@prova.it' as email, default
    assert reply.status_code == 200

    reply = login(tested_app, 'marco@prova.it', '123456')
    assert reply.status_code == 200

    reply = logout(tested_app)
    assert reply.status_code == 302
    assert reply.location == 'http://localhost/'

    # retrieve delete_user page without logging in before
    reply = tested_app.get('/delete_user')
    assert reply.status_code == 401

    reply = login(tested_app, email='marco@prova.it', password='123456')
    assert reply.status_code == 200

    # TODO create a run for the user and check that it is deleted once the user is deleted

    # retrieve delete_user page
    reply = tested_app.get('/delete_user')
    assert reply.status_code == 200

    # post incorrect password
    reply = tested_app.post('/delete_user', data=dict(password='000000'))
    assert reply.status_code == 401

    # post correct password and checking that the user has been deleted
    reply = tested_app.post('/delete_user', data=dict(password='123456'), follow_redirects=True)
    assert reply.status_code == 200

    with app.app_context():
        users = db.session.query(User).filter(User.email == 'marco@prova.it')
    assert users.first() is None



