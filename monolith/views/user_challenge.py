import datetime
from flask import Blueprint, redirect, render_template, request
from monolith.database import db, Run, Challenge
from monolith.auth import current_user, login_required

user_challenge = Blueprint('user_challenge', __name__)

@user_challenge.route('/create_challenge', methods=['GET', 'POST'])
@login_required
def create_challenge():
	runs = db.session.query(Run).filter(Run.runner_id == current_user.id)
	if request.method == 'POST':
		id_run = request.form['id_run']
		current_run = db.session.query(Run).filter(Run.id == id_run).first()
		new_challenge = Challenge()
		new_challenge.challenged = current_run
		new_challenge.start_date = datetime.datetime.utcnow()
		new_challenge.runner = current_user
		db.session.add(new_challenge)
		db.session.commit()
		return redirect('/challenges')
	return render_template("create_challenge.html", runs=runs, challenge_id=0)
	

@user_challenge.route('/complete_challenge', methods=['GET', 'POST'])
@login_required
def complete_challenge():
	if request.method == 'POST':
		id_challenge = request.form['id_challenge']
		current_challenge = db.session.query(Challenge).filter(Challenge.id == id_challenge).first()
		run_choice = db.session.query(Run).filter(Run.id == current_challenge.run_challenged_id).first()
		runs = db.session.query(Run).filter(Run.runner_id == current_challenge.runner_id).\
						filter(Run.start_date > current_challenge.start_date)
		return render_template("create_challenge.html", challenge_id=current_challenge.id, runs=runs, run_choice=run_choice)
	return redirect('/challenges')

@user_challenge.route('/terminate_challenge', methods=['GET','POST'])
@login_required
def terminate_challenge():
	if request.method == 'POST':
		id_challenger = request.form['id_challenger']
		id_challenge = request.form['id_challenge']
		current_challenge = db.session.query(Challenge).filter(Challenge.id == id_challenge).first()
		current_run = db.session.query(Run).filter(Run.id == id_challenger).first()
		current_challenge.challenger = current_run
		current_challenge.result = determine_result(current_challenge, current_run)
		db.session.commit()
		return redirect('/challenges')
	return redirect('/challenges')

def determine_result(current_challenge, current_run):
	challenged_run = db.session.query(Run).filter(Run.id == current_challenge.run_challenged_id).first()
	if challenged_run.distance == current_run.distance:
		return challenged_run.average_speed < current_run.average_speed
	elif challenged_run.distance < current_run.distance:
		return challenged_run.average_speed <= current_run.average_speed
	else:
		return False;

@user_challenge.route('/challenges')
@login_required
def challenges():
    challenges = db.session.query(Challenge).filter(Challenge.runner_id == current_user.id)
    if challenges.count()>0:
    	results = {}
    	for c in challenges:
    		challenged = (db.session.query(Run).filter(Run.id == c.run_challenged_id)).first()
    		challenger = (db.session.query(Run).filter(Run.id == c.run_challenger_id)).first()
    		results[c] = challenged, challenger
    	return render_template("challenges.html", results=results)
    return render_template("challenges.html")
