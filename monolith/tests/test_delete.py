from monolith.tests.utility import client, login, new_user, logout
from monolith.database import db, User


def test_delete(client):
    tested_app, app = client

    reply = new_user(tested_app)  # creates a user with 'marco@prova.it' as email, default
    assert reply.status_code == 200 or reply.status_code == 302

    reply = logout(tested_app)
    assert reply.status_code == 302

    # retrieve delete_user page without logging in before
    reply = tested_app.get('/delete_user')
    assert reply.status_code == 401

    reply = login(tested_app, email='marco@prova.it', password='123456')
    assert reply.status_code == 200

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




