from .home import home
from .auth import auth as _auth  # need to have monolith.auth visible or when we try to import it we get the blueprint
from .users import users
from .strava import strava
from .runs import runs
from .training_objectives import training_objectives
from .user_challenge import user_challenge
from .statistics import statistics
from .profile import profile
from .test import test


blueprints = [home,
              _auth,
              users,
              strava,
              runs,
              training_objectives,
              user_challenge,
              statistics,
              profile,
              test
              ]
