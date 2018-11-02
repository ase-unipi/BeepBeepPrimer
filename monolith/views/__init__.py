from .home import home
from .auth import auth
from .users import users
from .strava import strava
from .runs import runs


blueprints = [home, auth, users, strava, runs]
