from flask import Blueprint, render_template, request
from monolith.database import db, ReportPeriodicity
from monolith.auth import current_user, login_required
from monolith.forms import PeriodicReportForm


periodic_report = Blueprint('periodic_report', __name__)


@periodic_report.route('/periodic_report', methods=['GET', 'POST'])
@login_required
def _periodic_report():

    form = PeriodicReportForm()
    form.periodicity.choices = [(p.name, p.value) for p in ReportPeriodicity]

    if request.method == 'POST':
        current_user.report_periodicity = form.periodicity.data
        db.session.commit()

    form.periodicity.data = current_user.report_periodicity.name

    return render_template("periodic_report.html", form=form)
