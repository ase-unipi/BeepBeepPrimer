# pip3 install beautifulsoup4
from pyquery import PyQuery as pq
from monolith.tests.utils import ensure_logged_in
from monolith.database import User, Objectives, Run
from monolith.database import _setObjective
import random


def test_objective(client, db_instance):
    
    KILOMETERS = 1000

    # simulate login
    user = ensure_logged_in(client, db_instance)

    # generate some runs
    runs = []
    for i in ['1', '2']:
        run = Run()

        run.runner = user
        run.strava_id = i
        run.name = "Run " + i
        run.average_speed = float(i)
        #distance in meters
        run.distance = 2 * KILOMETERS
        run.elapsed_time = float(i)*float(i)*1000

        runs.append(run)

        db_instance.session.add(run)
    db_instance.session.commit()

    
    res = client.get("/")
    html=pq(res.data)
    total_distance = html("#tot_dist").html()

    assert total_distance == 10000