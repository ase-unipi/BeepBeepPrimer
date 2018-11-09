from flask import Blueprint, redirect, render_template, request
from monolith.database import db, User, Run, _delete_user
from monolith.auth import admin_required
from monolith.forms import UserForm, ChallengeForm
from flask_login import current_user, logout_user
from datetime import datetime

challenge = Blueprint('challenge', __name__)

@challenge.route("/challenge", methods=['POST'])
def post_challenge():

    form = ChallengeForm()
    '''
    dataRun = datetime.now()
    run = Run()
    
    run.average_heartrate = 140
    run.average_speed = 7
    run.distance = 3000
    run.elapsed_time = 2300
    run.name = 'run GREY'
    run.runner = current_user
    run.runner_id = current_user.id
    run.start_date = dataRun
    run.strava_id = 1
    run.total_elevation_gain = 80.5
    
    db.session.add(run)
    db.session.commit()
    '''
    runIds = form.data['runs']
    if runIds is None or len(runIds) != 1:
        return redirect('/?challengeError=Please select exactly one run to challenge')

    if current_user is not None and hasattr(current_user, 'id'):
        prev_challenged_run = db.session.query(Run).filter(Run.runner_id == current_user.id, Run.is_challenged == True).first()
        #found a previosly challenged run, gotta make it unchallenged and then challenge the next one
        if prev_challenged_run:
            prev_challenged_run.is_challenged = False
        new_challenge = db.session.query(Run).filter(Run.runner_id == current_user.id, Run.id == runIds[0]).first()
        new_challenge.is_challenged = True
        db.session.commit()
    else:
        return redirect("/login")
    
    return redirect("/")
