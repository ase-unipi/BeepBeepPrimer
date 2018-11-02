from flask import Blueprint, render_template, request
from monolith.database import db, Run
from monolith.auth import current_user, login_required


runs = Blueprint('runs', __name__)


@runs.route('/runs/<id>')
def _runs(id):
    run = None
    return render_template("runs.html", run=run)
