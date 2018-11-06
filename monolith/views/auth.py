from flask import Blueprint, render_template, redirect, request, flash, make_response
from flask_login import (current_user, login_user, logout_user,
                         login_required)
from stravalib import Client
from monolith.database import db, User
from monolith.forms import LoginForm
from monolith.views.home import strava_auth_url, home
auth = Blueprint('auth', __name__)


@auth.route('/strava_auth')
@login_required
def _strava_auth():
    code = request.args.get('code')
    client = Client()
    xc = client.exchange_code_for_token
    access_token = xc(client_id=auth.app.config['STRAVA_CLIENT_ID'],
                      client_secret=auth.app.config['STRAVA_CLIENT_SECRET'],
                      code=code)
    # check if access token exists
    users = db.session.query(User).filter(User.strava_token == access_token)
    if users.first() is not None:
        return make_response(render_template('strava_error.html', auth_url=strava_auth_url(home.app.config)), 409)
    current_user.strava_token = access_token
    db.session.add(current_user)
    db.session.commit()
    return redirect('/')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email, password = form.data['email'], form.data['password']
        q = db.session.query(User).filter(User.email == email)
        user = q.first()
        # print(user is None)
        # print(user.authenticate(password))
        if user is not None and user.authenticate(password):
            login_user(user)
            return redirect('/')
        else:
            flash('Wrong email or password', category='error')
            return make_response(render_template('login.html', form=form), 401)
    return render_template('login.html', form=form)


@auth.route("/logout")
def logout():
    if current_user.is_authenticated is True:
        logout_user()
    return redirect('/')
