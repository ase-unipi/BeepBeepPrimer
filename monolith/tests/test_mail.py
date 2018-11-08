from monolith.tests.utility import new_run, client, login, create_user, new_predefined_run
from monolith.database import db, User
from werkzeug.security import check_password_hash


def test_create_repo(client):
    tested_app, app = client
    reply = tested_app.post('/create_user', data=dict(email='mcriucc@gmail.com', firstname='mariacristina', lastname='uccheddu',
                                              password='ciao',
                                              age=23,
                                              weight=70,
                                              max_hr=120,
                                              rest_hr=60,
                                              vo2max=99), follow_redirects=True)

    assert reply.status_code == 200  # create_user success (it also redirect to login)

    assert login(tested_app, 'mcriucc@gmail.com', 'ciao').status_code == 200

    # now andrea@prova.it is logged in
    with app.app_context():
        user = db.session.query(User).filter(User.email == 'mcriucc@gmail.com').first()
        assert user is not None
        assert user.email == 'mcriucc@gmail.com'
        assert user.firstname == 'mariacristina'
        assert user.lastname == 'uccheddu'
        assert check_password_hash(user.password, 'ciao') is True
        assert user.age == 23
        assert user.weight == 70
        assert user.max_hr == 120
        assert user.rest_hr == 60
        assert user.vo2max == 99

    reply = tested_app.get('/report')
    assert reply.status_code == 200



