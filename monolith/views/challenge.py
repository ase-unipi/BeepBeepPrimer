from flask import Blueprint, redirect, render_template, request
from monolith.database import db, User, Run, _delete_user, Challenge
from sqlalchemy import func
from monolith.auth import admin_required
from monolith.forms import UserForm, ChallengeForm
from flask_login import current_user, logout_user
from datetime import datetime

challenge = Blueprint('challenge', __name__)

@challenge.route("/challenge", methods=['POST'])
def post_challenge():

    form = ChallengeForm()
  
    runIds = form.data['runs']
    if runIds is None or len(runIds) != 1:
        return redirect('/?challengeError=Please select exactly one run to challenge')

    if current_user is not None and hasattr(current_user, 'id'):
        prev_challenged_run = db.session.query(Challenge).filter(Challenge.runner_id == current_user.id).first()
        #found a previosly challenged run, gotta make it unchallenged and then challenge the next one
        if prev_challenged_run:
            db.session.delete(prev_challenged_run)
            if prev_challenged_run.run_id != int(runIds[0]):
                # I'm not unchallenging a run, but challenging a new one
                new_challenge = db.session.query(Run).filter(Run.runner_id == current_user.id, Run.id == runIds[0]).first()
                if new_challenge is not None:
                    challenge = Challenge()
                    challenge.run_id = runIds[0]
                    challenge.runner = current_user
                    challenge.runner_id = current_user.id
                    challenge.run = new_challenge
                    latest_id = db.session.query(func.max(Run.id)).scalar()
                    challenge.latest_run_id = latest_id
                    db.session.add(challenge)
            db.session.commit()
        else: # just challenge the new one
            new_challenge = db.session.query(Run).filter(Run.runner_id == current_user.id, Run.id == runIds[0]).first()
            if new_challenge is not None:
                challenge = Challenge()
                challenge.run_id = runIds[0]
                challenge.runner = current_user
                challenge.runner_id = current_user.id
                challenge.run = new_challenge
                latest_id = db.session.query(func.max(Run.id)).scalar()
                challenge.latest_run_id = latest_id
                db.session.add(challenge)
            db.session.commit()
    else:
        return redirect("/login")
    
    return redirect("/")

def create_run(id):
    
    dataRun = datetime.now()
    run = Run()
    
    run.average_heartrate = 140
    run.average_speed = 7
    run.distance = 3000
    run.elapsed_time = 2300
    run.name = 'run ' + str(id)
    run.runner = current_user
    run.runner_id = current_user.id
    run.start_date = dataRun
    run.strava_id = 1
    run.total_elevation_gain = 80.5
    
    db.session.add(run)
    db.session.commit()
    

