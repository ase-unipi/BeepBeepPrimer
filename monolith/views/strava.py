from flask import Blueprint, jsonify
from monolith.background import fetch_all_runs, send_all_mail
from monolith.auth import admin_required

strava = Blueprint('strava', __name__)


@strava.route('/fetch')
@admin_required
def fetch_runs():
    """using this function only for testing purpose"""
    res = fetch_all_runs.delay()
    res.wait()
    return jsonify(res.result)


@strava.route('/report')
def send_report():
    send_all_mail()
    return "Done"
