from flask import Blueprint, render_template
from stravalib import Client

from monolith.database import db, Run
from monolith.auth import current_user


@run.route('/run:<id>',methods=['GET'])
def get_run(id):
     if request.method == 'GET': 
        run = db.session.query(Run).filter(Run.id == id)
        return render_template("run.html", run=run)


	