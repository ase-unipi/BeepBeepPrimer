from flask import Blueprint, redirect, render_template, request
from monolith.database import db, Training_Objective
from monolith.auth import admin_required, login_required
from monolith.forms import TrainingObjectiveForm
from flask_login import current_user


training_objectives = Blueprint('training_objectives', __name__)


@training_objectives.route('/training_objectives', methods=['GET', 'POST'])
@login_required
def _training_objectives():
    form = TrainingObjectiveForm()
    objectives = None

    if request.method == 'POST':
        if form.validate_on_submit():
            new_objective = Training_Objective()
            form.populate_obj(new_objective)
            new_objective.runner_id = current_user.id
            db.session.add(new_objective)
            db.session.commit()

    if current_user is not None and hasattr(current_user, 'id'):
        objectives = db.session.query(Training_Objective).filter(Training_Objective.runner_id == current_user.id)

    return render_template("training_objectives.html", objectives=objectives, form=form)
