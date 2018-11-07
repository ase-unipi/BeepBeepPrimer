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
def get_runsData():
    toSend = dict()
    print(request)
    jsondata = request.get_json()
    print(jsondata)
    listRun = jsondata["runs"]
    print(listRun)
    runs = db.session.query(Run).filter(Run.id.in_(listRun)).all()
    print(runs)
    for run in runs:
        print(run)
        toSend[run.id] = [0, 0, 0, run.name]
        #Average Speed
        if jsondata["params"][0]:
            toSend[run.id][0] = run.average_speed
        #Distance
        if jsondata["params"][1]:
            toSend[run.id][1] = run.distance
        #Time 
        if jsondata["params"][2]:
            toSend[run.id][2] = run.elapsed_time
    print(toSend)
    return jsonify(toSend)