from flask import Blueprint, render_template
from flask_login import login_required

from monolith.database import db, Run
from monolith.auth import current_user

statistics = Blueprint('statistics', __name__)


@statistics.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    """Inside the template we retrieve data from run/statistics"""
    runs = db.session.query(Run).filter(Run.runner_id == current_user.id)
    return render_template("statistics.html", runs=runs)
