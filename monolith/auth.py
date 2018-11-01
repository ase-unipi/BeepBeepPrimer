import functools
from flask_login import current_user, LoginManager
from monolith.database import User
from flask import redirect


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
