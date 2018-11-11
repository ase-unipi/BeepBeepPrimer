from flask import Blueprint, redirect, render_template, request
from monolith.database import db, ReportPeriodicity
from monolith.auth import current_user, login_required
from monolith.views.auth import strava_deauth
from monolith.forms import ProfileForm
from werkzeug.security import generate_password_hash


profile = Blueprint('profile', __name__)


@profile.route('/profile', methods=['GET', 'POST'])
@login_required
def _profile():
    form = ProfileForm(obj=current_user)
    form.periodicity.choices = [(p.name, p.value) for p in ReportPeriodicity]
    form.password.render_kw = {'placeholder': 'YOUR OLD PASSWORD'}
    
    if request.method == 'POST' and form.validate_on_submit():
        tmp_password = current_user.password
        new_password = form.password.data

        form.populate_obj(current_user)
        current_user.report_periodicity = form.periodicity.data
        current_user.password = generate_password_hash(new_password) if new_password else tmp_password
        db.session.commit()

    form.periodicity.data = current_user.report_periodicity.name

    return render_template("profile.html",
                           form=form
                           )
