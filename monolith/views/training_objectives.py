from flask import Blueprint, redirect, render_template, request
from monolith.database import db, Run, Training_Objective
from monolith.auth import admin_required, login_required
from monolith.forms import TrainingObjectiveSetterForm, CompletedTrainingObjectiveForm, ActiveTrainingObjectiveForm, FailedTrainingObjectiveForm
from flask_login import current_user
from sqlalchemy.sql import between, func, text
from datetime import date


training_objectives = Blueprint('training_objectives', __name__)


@training_objectives.route('/training_objectives', methods=['GET', 'POST'])
@login_required
def _training_objectives():
    setter_form = TrainingObjectiveSetterForm()
    completed_form = CompletedTrainingObjectiveForm()
    active_form = ActiveTrainingObjectiveForm()
    failed_form = FailedTrainingObjectiveForm()

    completed_tos = None
    active_tos = None
    failed_tos = None

    if request.method == 'POST':
        if setter_form.validate_on_submit():
            new_objective = Training_Objective()
            setter_form.populate_obj(new_objective)
            new_objective.runner_id = current_user.id
            db.session.add(new_objective)
            db.session.commit()

    sql_active = text("""
    SELECT * FROM
    (
        -------------------------------------------------
        SELECT T.START_DATE, T.END_DATE, T.KILOMETERS_TO_RUN, (SUM(R.DISTANCE)/1000.0) AS TRAVELED_KILOMETERS, (T.KILOMETERS_TO_RUN - (SUM(R.DISTANCE)/1000.0)) AS KILOMETERS_LEFT
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
        SELECT T.START_DATE, T.END_DATE, T.KILOMETERS_TO_RUN, 0, T.KILOMETERS_TO_RUN
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
    
    WHERE TRAVELED_KILOMETERS < KILOMETERS_TO_RUN
    AND 
    DATE('NOW') <= END_DATE
    
    ORDER BY END_DATE    
    
    """.format(current_user.id,current_user.id))
    active_tos = db.engine.execute(sql_active)

    sql_completed = text("""
    SELECT * FROM
    (
        -------------------------------------------------
        SELECT T.START_DATE, T.END_DATE, T.KILOMETERS_TO_RUN, (SUM(R.DISTANCE)/1000.0) AS TRAVELED_KILOMETERS, (T.KILOMETERS_TO_RUN - (SUM(R.DISTANCE)/1000.0)) AS KILOMETERS_LEFT
        FROM TRAINING_OBJECTIVE T, RUN R

        WHERE R.RUNNER_ID = {}
        AND
        T.RUNNER_ID = R.RUNNER_ID
        AND
        R.START_DATE BETWEEN T.START_DATE AND T.END_date

        GROUP BY T.ID
        -------------------------------------------------        
    )
    
    WHERE TRAVELED_KILOMETERS >= KILOMETERS_TO_RUN
    
    ORDER BY END_DATE    
    """.format(current_user.id))
    completed_tos = db.engine.execute(sql_completed)

    sql_failed = text("""
    SELECT * FROM
    (
        -------------------------------------------------
        SELECT T.START_DATE, T.END_DATE, T.KILOMETERS_TO_RUN, (SUM(R.DISTANCE)/1000.0) AS TRAVELED_KILOMETERS, (T.KILOMETERS_TO_RUN - (SUM(R.DISTANCE)/1000.0)) AS KILOMETERS_LEFT
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
        SELECT T.START_DATE, T.END_DATE, T.KILOMETERS_TO_RUN, 0, T.KILOMETERS_TO_RUN
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
    
    WHERE TRAVELED_KILOMETERS < KILOMETERS_TO_RUN
    AND 
    DATE('NOW') > END_DATE
    
    ORDER BY END_DATE    
    
    """.format(current_user.id,current_user.id))
    failed_tos = db.engine.execute(sql_failed)

    return render_template("training_objectives.html",\
        active_tos=active_tos, completed_tos=completed_tos, failed_tos=failed_tos,\
        setter_form=setter_form, active_form=active_form, completed_form=completed_form, failed_form=failed_form)
