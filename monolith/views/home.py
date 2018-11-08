from flask import Blueprint, render_template, request, redirect

from stravalib import Client

from monolith.database import db, Run, User, Objectives
from monolith.auth import current_user
from monolith.forms import ObjectiveForm
from monolith.views.auth import *

home = Blueprint('home', __name__)

def sec2minsec(seconds):
    minutes = seconds // 60
    seconds = ((seconds / 60 ) - minutes) * 60

    return minutes, seconds

def _strava_auth_url(config):
    client = Client()
    client_id = config['STRAVA_CLIENT_ID']
    redirect = 'http://127.0.0.1:5000/strava_auth'
    url = client.authorization_url(client_id=client_id,
                                   redirect_uri=redirect)
    return url


@home.route('/')
def index():
    if request.args.get('comparisonError') is None:
        comparisonError = ""
    else:
        comparisonError = request.args.get('comparisonError')

    avgSpeed = 0
    objective_distance = 0
    tot_distance = 0
    elapsed_time = 0
    progress = 0
    avgminutes = 0
    avgsec = 0
    minutes = 0
    sec = 0

    if current_user is not None and hasattr(current_user, 'id'):
        runs = db.session.query(Run).filter(Run.runner_id == current_user.id)
        if runs.count() > 0:
            for run in runs:
                avgSpeed += run.average_speed
                tot_distance += run.distance
                elapsed_time += run.elapsed_time
            avgSpeed /=  runs.count()

            minutes, sec = sec2minsec(elapsed_time)

        objective = db.session.query(Objectives).filter(Objectives.user_id == current_user.id).first()
        if objective:
            objective_distance = objective.get_distance()*1000
    else:
        return redirect("/login")

    strava_auth_url = _strava_auth_url(home.app.config)

    if objective_distance - tot_distance > 0:
        progress = objective_distance - tot_distance
        percentage = (tot_distance/objective_distance)*100
    else:
        percentage = 100

    return render_template(
        "index.html", runs=runs,
        strava_auth_url=strava_auth_url,
        avgSpeed=avgSpeed,
        minutes = minutes,
        sec = sec,
        comparisonError=comparisonError,
        objective_distance=objective_distance, 
        tot_distance=tot_distance,
        progress=progress, 
        percentage=percentage
    )


@home.route('/objective', methods=['GET', 'POST'])
def set_objective():
    form = ObjectiveForm()

    if form.validate_on_submit():
        objective_distance = form.data['distance']
        q = db.session.query(User).filter(User.email == current_user.email)
        user = q.first()

        existing_objective = db.session.query(Objectives).filter(Objectives.user == user).first()
        if existing_objective is None:
            new_objective = Objectives()
            new_objective.distance = objective_distance
            new_objective.user = user

            db.session.add(new_objective)

        else:
            existing_objective.set_distance(objective_distance)

        db.session.commit()
        return redirect("/")

    return render_template('set_objective.html', form=form)
