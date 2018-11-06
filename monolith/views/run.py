from flask import Blueprint, render_template, flash, make_response
from flask_login import login_required

from monolith.database import db, Run

run = Blueprint('run', __name__)


@run.route('/run/<id>', methods=['GET'])
@login_required
def get_run(id):
    the_run = db.session.query(Run).filter(Run.id == id).first()
    if the_run is None:
        flash("Run not found", category='error')
        return make_response(render_template("run.html", run=the_run), 404)
    return render_template("run.html", run=the_run)
