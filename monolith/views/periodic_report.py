from flask import Blueprint, render_template, request
from monolith.database import db, REPORT_PERIODICITY
from monolith.auth import current_user, login_required
from monolith.forms import PeriodicReportForm


periodic_report = Blueprint('periodic_report', __name__)


@periodic_report.route('/periodic_report', methods=['GET', 'POST'])
@login_required
def _periodic_report():

    form = PeriodicReportForm()
    form.periodicity.choices = REPORT_PERIODICITY
    form.periodicity.default = current_user.report_periodicity

    if request.method == 'POST':
        current_user.report_periodicity = form.periodicity.data
        db.session.commit()

    return render_template("periodic_report.html", form=form)
