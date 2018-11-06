import datetime
from flask import Blueprint, redirect, render_template, request, url_for
from monolith.database import db, Run, Challenge
from monolith.auth import current_user, login_required

user_challenge = Blueprint('user_challenge', __name__)

@user_challenge.route('/create_challenge', methods=['GET', 'POST'])
@login_required
def create_challenge():
	if request.method == 'GET':
		challenges = db.session.query(Challenge).filter(Challenge.runner_id == current_user.id)
		if challenges.count()>0:
			results = {}
			for c in challenges:
				challenged = (db.session.query(Run).filter(Run.id == c.run_challenged_id)).first()
				challenger = (db.session.query(Run).filter(Run.id == c.run_challenger_id)).first()
				results[c] = challenged, challenger
			return render_template("create_challenge.html", results=results, challenge_id=None)
		return render_template("create_challenge.html", challenge_id=None)

	if request.method == 'POST':
		id_run = request.form['id_run']
		current_run = db.session.query(Run).filter(Run.id == id_run).first()
		new_challenge = Challenge()
		new_challenge.challenged = current_run
		new_challenge.start_date = datetime.datetime.utcnow()
		new_challenge.runner = current_user
		db.session.add(new_challenge)
		db.session.commit()
		runs = db.session.query(Run).filter(Run.runner_id == new_challenge.runner_id).\
							filter(Run.start_date > new_challenge.start_date)
		return render_template("create_challenge.html", challenge_id=new_challenge.id, runs=runs, run_challenged=current_run, run_challenger=None)
	return redirect(url_for('home.index'))
	

@user_challenge.route('/create_challenge/<id_challenge>', methods=['GET'])
@login_required
def complete_challenge(id_challenge):
	if request.method == 'GET':
		current_challenge = db.session.query(Challenge).filter(Challenge.id == id_challenge).first()
		try:
			run_challenged = db.session.query(Run).filter(Run.id == current_challenge.run_challenged_id).first()
		except AttributeError as e:
			return redirect(url_for('home.index'))
		if current_challenge.run_challenger_id is None:
			runs = db.session.query(Run).filter(Run.runner_id == current_challenge.runner_id).\
							filter(Run.start_date > current_challenge.start_date)
			return render_template("create_challenge.html", challenge_id=current_challenge.id, runs=runs, run_challenged=run_challenged, run_challenger=None)
		else:
			run_challenger = db.session.query(Run).filter(Run.id == current_challenge.run_challenger_id).first()
			return render_template("create_challenge.html", challenge_id=current_challenge.id, run_challenged=run_challenged, run_challenger=run_challenger)
	return redirect(url_for('home.index'))

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
		return redirect(url_for('user_challenge.complete_challenge', id_challenge=id_challenge))
	return redirect('/create_challenge')

def determine_result(current_challenge, current_run):
	challenged_run = db.session.query(Run).filter(Run.id == current_challenge.run_challenged_id).first()
	if challenged_run.distance == current_run.distance:
		return challenged_run.average_speed < current_run.average_speed
	elif challenged_run.distance < current_run.distance:
		return challenged_run.average_speed <= current_run.average_speed
	else:
		return False;
