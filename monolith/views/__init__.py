from .home import home
from .auth import auth
from .users import users
from .strava import strava
from .run import run
#from .statistics import statistics

blueprints = [home, auth, users, strava, run] #, statistics]
