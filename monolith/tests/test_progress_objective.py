# pip3 install beautifulsoup4
from pyquery import PyQuery as pq

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

    r = db_instance.session.query(User)

    res = client.get("/")
    html=pq(res.data)
    mydata=html("#avgSpd")
    print("*************")
    print(mydata)
    print("*************")