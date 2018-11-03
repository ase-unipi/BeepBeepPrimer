from .home import home
from .auth import auth
from .users import users
from .strava import strava
from .errors import errors


blueprints = [home, auth, users, strava, errors]
