from .home import home
from .auth import auth
from .users import users
from .strava import strava
from .runs import runs
from .training_objectives import training_objectives
from .test import test
from .user_challenge import user_challenge
from .statistics import statistics

blueprints = [home, auth, users, strava, runs, training_objectives, test, user_challenge, statistics]
