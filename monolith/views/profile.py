from flask import Blueprint, redirect, render_template, request
from monolith.database import db
from monolith.auth import current_user, login_required
from monolith.views.auth import strava_deauth
from monolith.forms import UserForm
from werkzeug.security import generate_password_hash


profile = Blueprint('profile', __name__)


@profile.route('/profile', methods=['GET', 'POST'])
def _profile():
    form = UserForm(obj=current_user)
    form.email.render_kw = {'disabled': 'disabled'}
    # form.password.render_kw = {'disabled': 'disabled'}
    form.password.render_kw = {'placeholder': 'YOUR OLD PASSWORD'}

    welcome_text = 'Welcome ' + current_user.firstname + ' ' + current_user.lastname 
    
    if request.method == 'POST' and form.validate_on_submit():
        tmp_password = current_user.password
        new_password = form.password.data

        form.populate_obj(current_user)
        current_user.password = generate_password_hash(new_password) if new_password else tmp_password
        db.session.commit()

    return render_template("profile.html",
                           form=form,
                           welcome_text=welcome_text,
                           )
