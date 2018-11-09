from monolith.database import User, Run
from monolith.forms import ChallengeForm
from monolith.tests.utils import ensure_logged_in


def test_challenge_run(client, db_instance):

    # simulate login
    user = ensure_logged_in(client, db_instance)

    # generate some runs
    runs = []
    for i in ['1', '2', '3']:
        run = Run()

        run.runner = user
        run.strava_id = i
        run.name = "Run " + i
        if i != '3':
            run.average_speed = float(i)
            run.elapsed_time = float(i)*1000
        else:
            run.average_speed = 0
            run.elapsed_time = 1

        runs.append(run)

        db_instance.session.add(run)
    db_instance.session.commit()

    # route back to index page
    res = client.post(
        '/challenge',
        data={
            'runs': ['1']
        },
        follow_redirects=True
    )

    challenged = db.session.query(Run).filter(Run.id==1, user.id == Run.runner_id).first()
    assert challenged
    assert challenged.is_challenged == True

    
