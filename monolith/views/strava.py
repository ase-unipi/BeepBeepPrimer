from flask import Blueprint, request, redirect
from monolith.background import fetch_runs_for_user
from monolith.auth import strava_token_required, login_required
from flask_login import current_user

strava = Blueprint('strava', __name__)


@strava.route('/fetch')
@strava_token_required
@login_required
def fetch():
    res = fetch_runs_for_user.delay(current_user.id)
    res.wait()
    print(request.referrer)
    if request.referrer is not None and 'login' not in request.referrer:
        return redirect(request.referrer)
    return redirect('/')
