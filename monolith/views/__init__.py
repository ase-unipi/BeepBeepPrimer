from .home import home
from .auth import auth
from .users import users
from .strava import strava
from .runs import runs
from .statistics import statistics

blueprints = [home, auth, users, strava, runs, statistics]
