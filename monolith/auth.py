import functools
from flask_login import current_user, LoginManager
from monolith.database import User, db
from flask import redirect
from stravalib import exc
#packages below are used for caching purposes
from flask import make_response
from functools import wraps, update_wrapper
from datetime import datetime

login_manager = LoginManager()


def admin_required(func):
    @functools.wraps(func)
    def _admin_required(*args, **kw):
        admin = current_user.is_authenticated and current_user.is_admin
        if not admin:
            return login_manager.unauthorized()
        return func(*args, **kw)
    return _admin_required


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(user_id)
    if user is not None:
        user._authenticated = True
    return user


def login_required(func):
    @functools.wraps(func)
    def _login_required(*args, **kw):
        if current_user is not None and current_user.is_authenticated:
            return func(*args, **kw)
        return redirect('/')
    return _login_required

#decorator used to avoid caching a page content (i.e: as in the case of plots for statistics)
def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


def strava_token_required(func):
    @functools.wraps(func)
    def _strava_token_required(*args, **kw):
        try:
            return func(*args, **kw)
        except exc.AccessUnauthorized:
            if current_user is not None and hasattr(current_user, 'id'):
                q = db.session.query(User).filter(User.id == current_user.id)
                user = q.first()
                user.strava_token = None
                db.session.add(user)
                db.session.commit()
            return redirect('/')
    return _strava_token_required
