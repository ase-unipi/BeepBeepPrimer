import unittest

from flask import request
from monolith.app import create_app
from monolith.database import db, User, Run, Objectives, _delete_user
import random



class TestApp(unittest.TestCase):

    def test_delete_user1(self):
        app = create_app()
        #test_app = app.test_client()

        # creating mock user
        email = 'mock' + str(random.randint(1, 101)) + '@mock.com'
        password = 'mock'
        example = User()
        example.email = email
        example.set_password(password)

        with app.app_context():
            db.session.add(example)
            db.session.commit()

            _delete_user(example)
            user = db.session.query(User).filter(User.email == email).first()
            self.assertEqual(user, None)

    def test_delete_user2(self):
        app = create_app()

        # creating mock user
        email = 'mock' + str(random.randint(1, 101)) + '@mock.com'
        password = 'mock'
        example = User()
        example.email = email
        example.set_password(password)

        runs_id =['1', '2', '3']

        objective = Objectives()
        objective.distance = 1000
        objective.user = example

        with app.app_context():
            db.session.add(example)

            for id in runs_id:
                run = Run()
                run.runner = example
                run.strava_id = id
                db.session.add(run)

            db.session.add(objective)

            db.session.commit()
            user_id = example.get_id()

            _delete_user(example)
            user = db.session.query(User).filter(User.email == email).first()
            self.assertEqual(user, None)

            run = db.session.query(Run).filter(Run.runner_id == user_id).first()
            self.assertEqual(run, None)

            objective = db.session.query(Objectives).filter(Objectives.user_id == user_id).first()
            self.assertEqual(objective, None)

