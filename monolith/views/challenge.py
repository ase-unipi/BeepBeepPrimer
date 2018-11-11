from flask import Blueprint, render_template, request, make_response, flash
from flask_login import current_user, login_required
from werkzeug.utils import redirect

from monolith.database import db, Run, Challenge, User
from monolith.forms import ChallengeForm


challenge = Blueprint('challenge', __name__)



@challenge.route('/challenge', methods=['GET'])
@login_required
def show_challenge():
    challenges = db.session.query(Challenge).filter(Challenge.runner_id == current_user.id)
    return render_template('challenge.html', challenges=challenges)

@challenge.route('challenge/<id>',methods=['GET'])
@login_required
def confront_run(id):
    win_distance = ""
    win_time = ""
    win_avg_speed = ""
    run = db.session.query(Challenge).filter(Challenge.id == id)
    if run.first() is None:
        flash('There are no challenge for this run', category='error')
        return make_response(render_template('create_challenge.html'), 409)
    else:
        run = run.first()
        confront = db.session.query(Run).filter(Challenge.confront == run.confront)
        confront = confront.first()
        if confront.distance > run.distance:
            win_distance = "You win for the distance field"
        if confront.elapsed_time < run.elapsed_time:
            win_time = "You win for the time"
        if confront.average_speed > run.average_speed:
            win_avg_speed = "You win for the average speed"
    return render_template('comparechallenge.html', win_avg_speed=win_avg_speed, win_distance=win_distance, win_time=win_time )



@challenge.route('/create_challenge', methods=['GET','POST'])
@login_required
def challenge_create():

    form = ChallengeForm()
    runs = db.session.query(Run).all()
    if request.method == 'POST':
            option = request.form['name']
            c = db.session.query(Run).filter(Run.name == option)
            num = db.session.query(Run).count() + 1
            if c.first() is None:
                flash('The run does not exists', category='error')
                return make_response(render_template('create_challenge.html', form=form), 409)
            else:
                c = c.first()
                new_challenge = Challenge()
                new_challenge.setname(option)
                new_challenge.setconfront(num)
                new_challenge.setdistance(c.distance)
                new_challenge.setelapsedtime(c.elapsed_time)
                new_challenge.setaveragespeed(c.average_speed)
                new_challenge.setrunner(c.runner)
                db.session.add(new_challenge)
                db.session.commit()
                return redirect('/challenge')

    return render_template('create_challenge.html', form=form , runs=runs)








