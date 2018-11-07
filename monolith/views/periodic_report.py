from flask import Blueprint, render_template, request
from monolith.database import db
from monolith.auth import current_user, login_required


periodic_report = Blueprint('periodic_report', __name__)


@periodic_report.route('/periodic_report', methods=['GET', 'POST'])
@login_required
def _periodic_report():
    
    return render_template("periodic_report.html")
