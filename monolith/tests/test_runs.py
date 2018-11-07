import unittest

from flask import request
from monolith.app import create_app
from monolith.views.runs import _runs
from flask import Blueprint, render_template
from monolith.database import db, Run, User, _delete_user
from monolith.auth import current_user
from werkzeug import ImmutableMultiDict
import random

import json
from flask import request, jsonify


class TestApp(unittest.TestCase):

	#if any of runs were deleted
	def test_runs1(self):
		app = create_app()
		email = 'mock' + str(random.randint(1, 101)) + '@mock.com'
		password = 'mock'
		example = User()
		example.email = email
		example.set_password(password)


		runs_id =['1', '2', '3', '4', '5', '6', '7']

		with app.app_context():
			db.session.add(example)

			for i in runs_id:
				run = Run()
				run.runner = example
				run.strava_id = i
				db.session.add(run)
			
			db.session.commit()
			user_id = example.get_id()


			previous_run = db.session.query(Run).filter(Run.runner_id == example.get_id(), Run.id<7).order_by(Run.id.desc()).first()
			self.assertEqual(previous_run.id, 6)

			q = db.session.query(Run).filter(Run.runner_id == example.get_id(), Run.id == 4)
			q.delete(synchronize_session=False)
			db.session.commit()
			previous_run = db.session.query(Run).filter(Run.runner_id == example.get_id(), Run.id<5).order_by(Run.id.desc()).first()
			self.assertEqual(previous_run.id, 3)

			_delete_user(example)
            


	#if given id is larger than all run's  id
	def test_runs2(self):
		app = create_app()
		email = 'mock' + str(random.randint(1, 101)) + '@mock.com'
		password = 'mock'
		example = User()
		example.email = email
		example.set_password(password)


		runs_id =['1', '2', '3', '4', '5', '6', '7']

		with app.app_context():
			db.session.add(example)

			for i in runs_id:
				run = Run()
				run.runner = example
				run.strava_id = i
				db.session.add(run)
			
			db.session.commit()
			user_id = example.get_id()
			runId=150

			run = db.session.query(Run).filter(Run.runner_id == example.get_id(), Run.id == runId).first()
			self.assertEqual(run, None)

			_delete_user(example)
