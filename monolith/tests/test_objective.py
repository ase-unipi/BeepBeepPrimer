from monolith.database import User, Objectives, Run
from monolith.database import _setObjective
import random

def test_objective(client, db_instance):

    client.post(
        '/create_user',
        data=dict(
            email='example@test.com',
            firstname='Jhon',
            lastname='Doe',
            password='password',
            age='22',
            weight='75',
            max_hr='150',
            rest_hr='60',
            vo2max='10'
        ),
        follow_redirects=True
    )

    user = db_instance.session.query(User).first()
    db_instance.session.add(user)

    runs_id = ['1', '2']

    for i in runs_id:
        run = Run()
        run.runner = user
        run.strava_id = i
        run.distance = 1000
        db_instance.session.add(run)

    db_instance.session.commit()

    objective_distance = 1000
    _setObjective(user, objective_distance)

    assert db_instance.session.query(Objectives).first().distance == 1000