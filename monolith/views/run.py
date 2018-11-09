from flask import Blueprint, render_template, abort, request, jsonify
from flask_login import login_required

from monolith.database import db, Run

run = Blueprint('run', __name__)


@run.route('/run/<id>', methods=['GET'])
@login_required
def get_run(id):
    the_run = db.session.query(Run).filter(Run.id == id).first()
    if the_run is None:
        abort(404)
    return render_template("run.html", run=the_run)


@run.route('/run/statistics', methods=['GET', 'POST'])
@login_required
def get_runs_data():
    """ This function takes as input (with a POST) one JSON dict
    that contains: {
                    'runs': [run_id_1, run_id_2, ...]
                    'params: [bool1, bool2, bool3]
                        }
    bool1: true if avg speed is required
    bool2: true if distance is required
    bool3: true if elapsed time is required

    And returns another json:
        {
            run_id_1: [avg_speed, distance, time, run_name]
            run_id_2: ...
            .
            .
            .
        }
    values are 0 if not required
    """
    to_send = dict()
    print(request)
    json_data = request.get_json()
    print(json_data)
    runs_id_list = json_data["runs"]
    print(runs_id_list)
    runs = db.session.query(Run).filter(Run.id.in_(runs_id_list)).all()
    print(runs)
    for run in runs:
        print(run)
        to_send[run.id] = [0, 0, 0, run.name]
        # Average Speed
        if json_data["params"][0]:
            to_send[run.id][0] = run.average_speed
        # Distance
        if json_data["params"][1]:
            to_send[run.id][1] = run.distance
        # Time
        if json_data["params"][2]:
            to_send[run.id][2] = run.elapsed_time
    print(to_send)
    return jsonify(to_send)
