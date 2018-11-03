from .home import home
from .auth import auth
from .users import users
from .strava import strava
from .runs import runs
from .user_challenge import user_challenge


blueprints = [home, auth, users, strava, runs, user_challenge]
