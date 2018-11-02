from flask import Blueprint, jsonify
from monolith.background import fetch_all_runs
from monolith.auth import strava_token_required


strava = Blueprint('strava', __name__)


@strava.route('/fetch')
@strava_token_required
def fetch_runs():
    res = fetch_all_runs.delay()
    res.wait()
    return jsonify(res.result)
