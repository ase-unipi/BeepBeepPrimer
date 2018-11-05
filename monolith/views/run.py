from flask import Blueprint, render_template
from flask_login import login_required

from monolith.database import db, Run

run = Blueprint('run', __name__)


@run.route('/run/<id>', methods=['GET'])
@login_required
def get_run(id):
    run = db.session.query(Run).filter(Run.id == id)
    return render_template("run.html", run=run)
