from monolith.tests.utility import client, login, create_user, logout


def test_users_list(client):
    tested_app, app = client

    assert login(tested_app, email='example@example.com', password='admin').status_code == 200

    # only admin can get this page
    assert tested_app.get('/users').status_code == 200

    reply = logout(tested_app)
    assert reply.status_code == 200

    assert create_user(tested_app).status_code == 200

    assert login(tested_app, email='marco@prova.it', password='123456').status_code == 200

    # marco@prova.it is not admin
    assert tested_app.get('/users').status_code == 401


