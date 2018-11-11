from flask import Blueprint, render_template, request, make_response, flash
from flask_login import current_user, login_required
from werkzeug.utils import redirect

from monolith.database import db, Run, Challenge, User
from monolith.forms import ChallengeForm


challenge = Blueprint('challenge', __name__)



@challenge.route('/challenge', methods=['GET'])
@login_required
def show_challenge():
    challenges = db.session.query(Challenge).filter(Challenge.runner_id == current_user.id).all()
    return render_template('challenge.html', challenges=challenges)



@challenge.route('/create_challenge', methods=['GET','POST'])
@login_required
def challenge_create():

    form = ChallengeForm()
    runs = db.session.query(Run).all()
    if request.method == 'POST':
        if form.validate_on_submit():
            option = request.form['name']
            c = db.session.query(Run).filter(Run.name == option).first()
            num = db.session.query(Run).count() + 1
            if c.first() is None:
                flash('The run does not exists', category='error')
                return make_response(render_template('create_challenge.html', form=form), 409)
            else:
                new_challenge = Challenge()
                new_challenge.setname(option)
                new_challenge.setconfront(num)
                new_challenge.setdistance(c.distance)
                new_challenge.setelapsedtime(c.elapsed_time)
                new_challenge.setaveragespeed(c.average_speed)
                new_challenge.setrunner(c.runner_id)
                db.session.add(new_challenge)
                db.session.commit()
                return redirect('/challenge')

    return render_template('create_challenge.html', form=form , runs=runs)








