from flask import Blueprint, redirect, render_template, request
from monolith.database import db, User, Run
from monolith.auth import current_user
from monolith.forms import UserForm
from monolith.views.auth import strava_deauth


users = Blueprint('users', __name__)


@users.route('/users')
def _users():
    users = db.session.query(User)
    return render_template("users.html", users=users)


@users.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = UserForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            new_user.set_password(form.password.data) #pw should be hashed with some salt
            new_user.average_speed = 0
            print(new_user)
            db.session.add(new_user)
            db.session.commit()
            return redirect('/users')

    return render_template('create_user.html', form=form)


@users.route('/remove_user', methods=['GET', 'POST'])
def delete_user():

    if request.method == 'POST':
        if current_user is not None and hasattr(current_user, 'id'):
            db.session.delete(current_user)
            db.session.commit()
            strava_deauth()
            return redirect('/')

