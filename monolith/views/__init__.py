from .home import home
from .auth import auth
from .users import users
from .strava import strava
from .runs import runs
from .training_objectives import training_objectives
from .test import test

blueprints = [home, auth, users, strava, runs, training_objectives, test]
