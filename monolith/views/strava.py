from flask import Blueprint, jsonify
from monolith.background import fetch_all_runs, send_all_mail

strava = Blueprint('strava', __name__)


@strava.route('/fetch')
def fetch_runs():
    res = fetch_all_runs.delay()
    res.wait()
    return jsonify(res.result)


@strava.route('/report')
def send_report():
    send_all_mail()
    return "Done"
