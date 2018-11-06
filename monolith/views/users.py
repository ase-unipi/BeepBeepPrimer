from flask import Blueprint, redirect, render_template, request, flash, make_response, url_for
from flask_login import fresh_login_required, current_user, logout_user, login_user
from flask_login import LoginManager, fresh_login_required, confirm_login
from monolith.database import db, User, Run
from monolith.auth import admin_required
from monolith.forms import UserForm, DeleteForm
from monolith.views.home import home, strava_auth_url


users = Blueprint('users', __name__)


@users.route('/users')
@admin_required
def _users():
    users = db.session.query(User)
    return render_template("users.html", users=users)


@users.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if current_user is not None and hasattr(current_user,'id'):     ## The connected user cannot create other users
        return redirect('/')          ## They are redirect instantaneously to the main page

    form = UserForm()
    if request.method == 'POST':

        if form.validate_on_submit():
            new_user = User()
            form.populate_obj(new_user)
            c = db.session.query(User).filter(new_user.email == User.email)
            if c.first() is None:
                new_user.set_password(form.password.data)  # pw should be hashed with some salt
                db.session.add(new_user)
                db.session.commit()
                # return redirect(url_for('auth.login'))
                login_user(new_user)
                
                ## This sets the current session as fresh.
                #  Sessions become stale when they are reloaded from a cookie
                confirm_login()
                return redirect(strava_auth_url(home.app.config))
            else:
                flash('Already existing user', category='error')
                return make_response(render_template('create_user.html', form=form), 409)

    return render_template('create_user.html', form=form)


@users.route('/delete_user', methods=['GET', 'POST'])
@fresh_login_required       ## The fresh login provide the possibility to not have problem with the cookies
def delete_user():
    form = DeleteForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.authenticate(form.password.data) and hasattr(current_user, 'id'):
                runs = db.session.query(Run).filter(Run.runner_id == current_user.id)

                for run in runs.all():
                    db.session.delete(run)

                db.session.delete(current_user)
                db.session.commit()
                
                logout_user()  # This will also clean up the remember me cookie if it exists.
                return redirect('/')
            else:
                flash("Incorrect password", category='error')
                return make_response(render_template("delete_user.html", form=form), 401)

    return render_template("delete_user.html", form=form)
