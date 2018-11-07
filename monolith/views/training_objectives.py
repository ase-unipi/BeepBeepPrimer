from flask import Blueprint, redirect, render_template, request
from monolith.database import db, Run, Training_Objective
from monolith.auth import admin_required, login_required
from monolith.forms import TrainingObjectiveSetterForm, TrainingObjectiveVisualizerForm
from flask_login import current_user
from sqlalchemy.sql import between, func, text
from datetime import date


training_objectives = Blueprint('training_objectives', __name__)


@training_objectives.route('/training_objectives', methods=['GET', 'POST'])
@login_required
def _training_objectives():
    setter_form = TrainingObjectiveSetterForm()
    visualizer_form = TrainingObjectiveVisualizerForm()

    list_of_tos = None

    if request.method == 'POST':
        if setter_form.validate_on_submit():
            new_objective = Training_Objective()
            setter_form.populate_obj(new_objective)
            new_objective.runner_id = current_user.id
            db.session.add(new_objective)
            db.session.commit()

    sql_text = text("""
    SELECT
        START_DATE,
        END_DATE,
        ROUND(KILOMETERS_TO_RUN, 3),
        ROUND(TRAVELED_KILOMETERS, 3),
        ROUND(KILOMETERS_LEFT, 3),
        IS_EXPIRED
    FROM
    (
        -------------------------------------------------
        SELECT T.START_DATE, T.END_DATE, T.KILOMETERS_TO_RUN, (SUM(R.DISTANCE)/1000.0) AS TRAVELED_KILOMETERS, (T.KILOMETERS_TO_RUN - (SUM(R.DISTANCE)/1000.0)) AS KILOMETERS_LEFT, (T.END_DATE < DATE('NOW')) AS IS_EXPIRED
        FROM TRAINING_OBJECTIVE T, RUN R

        WHERE R.RUNNER_ID = {}
        AND
        T.RUNNER_ID = R.RUNNER_ID
        AND
        R.START_DATE BETWEEN T.START_DATE AND T.END_date

        GROUP BY T.ID
        -------------------------------------------------
    
            UNION ALL
        
        -------------------------------------------------    
        SELECT T.START_DATE, T.END_DATE, T.KILOMETERS_TO_RUN, 0, T.KILOMETERS_TO_RUN, T.END_DATE < DATE('NOW')
        FROM TRAINING_OBJECTIVE T

        WHERE T.ID IN
        (
            SELECT T.ID
            FROM TRAINING_OBJECTIVE T LEFT JOIN RUN R ON
            (T.RUNNER_ID = R.RUNNER_ID AND R.START_DATE BETWEEN T.START_DATE AND T.END_DATE)
            
            WHERE T.RUNNER_ID = {}
            
            GROUP BY T.ID
            HAVING COUNT(R.ID)=0
        )
        -------------------------------------------------
        
    )
   
    ORDER BY START_DATE, END_DATE
    
    """.format(current_user.id,current_user.id))
    list_of_tos = db.engine.execute(sql_text)

    return render_template("training_objectives.html",list_of_tos=list_of_tos,setter_form=setter_form,visualizer_form=visualizer_form)
