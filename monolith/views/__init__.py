from .home import home
from .auth import auth as a  # need to have monolith.auth visible or when we try to import it we get the blueprint
from .users import users
from .strava import strava


blueprints = [home, a, users, strava]
