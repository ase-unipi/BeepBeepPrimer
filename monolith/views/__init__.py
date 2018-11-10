from .home import home
from .auth import auth
from .users import users
from .strava import strava
from .objectives import objectives
from .run import run
from .statistics import statistics
from .report import report

blueprints = [home, auth, users, strava, run, statistics, objectives, report]
