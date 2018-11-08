import unittest

from monolith.app import create_app
from monolith.database import db, User, Objectives, _setObjective, _delete_user
import random


class TestApp(unittest.TestCase):

    def test_create_user(self):
        app = create_app()

        email = 'mock' + str(random.randint(1, 101)) + '@mock.com'
        password = 'mock'
        example = User()
        example.email = email
        example.set_password(password)

        with app.app_context():
            db.session.add(example)
            db.session.commit()

            user = db.session.query(User).filter(User.email == email).first()
            distance = 1000
            _setObjective(user, distance)

            objective = db.session.query(Objectives).filter(Objectives.user_id == user.id).first()
            if objective:
                self.assertEqual(1000, objective.get_distance())
            else:
                self.fail()

            _delete_user(user)


