from flask import Blueprint, render_template, request
from monolith.database import db, Run
from monolith.auth import current_user, login_required


runs = Blueprint('runs', __name__)


@runs.route('/runs/<id>', methods=['GET'])
@login_required
def run(id):
    name    = None
    date    = None
    headers = None
    values  = None

    run = db.session.query(Run).filter(Run.runner_id == current_user.id, Run.id == id).first()
    if run is not None:
        name    = run.name
        date    = run.start_date.strftime('%A %d/%m/%y at %H:%M')
        headers = ['Distance (m)', 'AVG Speed (m/s)', 'Elapsed Time (s)', 'Elevation (m)']
        values  = [run.distance, run.average_speed, run.elapsed_time, run.total_elevation_gain]
    
    return render_template("runs.html", name=name, date=date, headers=headers, values=values)
