from unittest import mock
from monolith.database import User, Run
from tests.conftest import mocked_result
from tests.test_core import test_create_runs

#test that no runs are returned if accessing /runs before logging in
def test_no_runs(client):
    rv = client.get('/runs')
    #check if a 404 is indeed returned
    assert b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>404 Not Found</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.</p>\n' in rv.data;



#testing if the user interface is properly generated (i.e: css, images..)
def test_graphical_ui_generated(client, background_app, db_instance, celery_session_worker):
    test_create_runs(client, background_app, db_instance, celery_session_worker)

    #daniele: we have created a user, runs and are now logged in. let's see if we actualy manage to see our nice runs
    rv = client.get('/runs/3')

    #header stuff

    assert b'<link rel="stylesheet" href="/static/style.css">' in rv.data

    assert b'<link rel="shortcut icon" href="/static/favicon.ico">' in rv.data

    assert b'<li><img src="/static/nav_logo.png" class="logo" /></li>' in rv.data

    #now let's see if the navbar is visible
    assert b'<li><a href="/">Home</a></li>' in rv.data
    assert b'<li><a href="/create_challenge">Challenges</a></li>'in rv.data
    assert b'<li><a href="/training_objectives">Training Objectives</a></li>'in rv.data
    assert b'<li><a href="/statistics">Statistics</a></li>'in rv.data
    assert b'<li class="float-right"><a href="/logout">Logout</a></li>'in rv.data
    assert b'<li class="float-right"><a href="/fetch">Fetch new Runs</a></li>'in rv.data

    #and check whether the footer is also visible

    assert b'<li><a href="https://github.com/MFranceschi6">Matteo Franceschi</a></li>' in rv.data
    assert b'<li><a href="https://github.com/edoBaldini">Edoardo Baldini</a></li>' in rv.data
    assert b'<li><a href="https://github.com/Albertomac">Alberto Ottimo</a></li>' in rv.data
    assert b'<li><a href="https://github.com/deselmo">William Guglielmo</a></li>' in rv.data
    assert b'<li><a href="https://github.com/DanyEle">Daniele Gadler</a></li>' in rv.data
    assert b'<li><a href="https://github.com/lorenz944">Lorenzo Casalini</a></li>' in rv.data
    assert b'<li><a href="https://github.com/SuperNabla95">Francesco Tosoni</a></li>' in rv.data
    assert b'<li><a href="https://github.com/Polletz">Riccardo Paoletti</a></li>' in rv.data
    assert b'<li><a class="float-right" href="https://github.com/MFranceschi6/BeepBeepPrimer">Butter Group S.R.L.</a></li>' in rv.data

    #check whether the feature to create a challenge is indeed visible
    assert b'<form action="/create_challenge" method="post">' in rv.data
    assert b'<td class="text-center">' in rv.data
    assert b'<a href="#" onclick="document.forms[0].submit()">' in rv.data
    assert b'<img class="icon" src="/static/challenge.png"/>' in rv.data
    assert b'</form>' in rv.data





#testing if every single field of the 'run' page is created and populated correctly, with the values contained in the DB
def test_functional_elements_generated(client, background_app, db_instance, celery_session_worker):
    test_create_runs(client, background_app, db_instance, celery_session_worker)

    # daniele: we have created a user, runs and are now logged in. let's see if we actualy manage to see our nice runs
    rv = client.get('/runs/3')

    # run header properly generated
    assert b'<li class="float-right"><a href="/profile">Hi emaill@email.com </a></li>' in rv.data

    assert b'<h3 class="text-center textPumpkingDark">Wednesday 02/05/18 at 12:15</h3>' in rv.data

    # run name properly set
    assert b'<h1 class="text-center textJeansDark">Happy Friday</h1>' in rv.data

    # distance properly set
    assert b'<td class="text-center">24931.4</td>' in rv.data

    # average speed properly set
    assert b'<td class="text-center">5.54</td>' in rv.data

    # duration properly set
    assert b'<td class="text-center">4500.0</td>' in rv.data

    # elevation gain properly set
    assert b'<td class="text-center">0.0</td>' in rv.data


#now check if the whole page is generated properly with the data of the runs contained in the DB
def test_full_page_generation(client, background_app, db_instance, celery_session_worker):
    test_create_runs(client, background_app, db_instance, celery_session_worker)

    # daniele: login is fine, now let's see if we actualy manage to see our nice runs
    rv = client.get('/runs/3')
    #print(rv.data)
    #the whole page generation for run with ID = 3
    assert b'<html>\n<head>\n  <link rel="stylesheet" href="/static/style.css">\n  <link rel="shortcut icon" href="/static/favicon.ico">\n</head>\n<body>\n  <ul class="navbar">\n    <li><img src="/static/nav_logo.png" class="logo" /></li>\n    <li><a href="/">Home</a></li>\n    \n    \n      <li><a href="/create_challenge">Challenges</a></li>\n      <li><a href="/training_objectives">Training Objectives</a></li>\n      <li><a href="/statistics">Statistics</a></li>\n      <li class="float-right"><a href="/logout">Logout</a></li>\n      \n      \n        <li class="float-right"><a href="/fetch">Fetch new Runs</a></li>\n      \n      \n      <li class="float-right"><a href="/profile">Hi emaill@email.com </a></li>\n    \n    \n  \n  </ul>\n  <section>\n    <div class="bodyContainer">\n      <div class="bodyContent">\n\n  <div class="content">\n    <h1 class="text-center textJeansDark">Happy Friday</h1>\n    <h3 class="text-center textPumpkingDark">Wednesday 02/05/18 at 12:15</h3>\n    \n    <table>\n      <thead>\n        <tr>\n          \n            <th>Distance (m)</th>\n          \n            <th>AVG Speed (m/s)</th>\n          \n            <th>Elapsed Time (s)</th>\n          \n            <th>Elevation (m)</th>\n          \n          <th>Actions</th>\n        </tr>\n      </thead>\n      <tbody>\n        <tr>\n          \n            <td class="text-center">24931.4</td>\n          \n            <td class="text-center">5.54</td>\n          \n            <td class="text-center">4500.0</td>\n          \n            <td class="text-center">0.0</td>\n          \n            <form action="/create_challenge" method="post">\n              <td class="text-center">\n                 <input type="hidden" name="id_run" value=3 />\n                  <a href="#" onclick="document.forms[0].submit()"> \n                  <img class="icon" src="/static/challenge.png"/>\n                </a>\n              </td>\n            </form> \n        </tr>\n      </tbody>\n    </table>\n  </div>\n\n    </div>\n  </div>\n  </section>\n  <ul class="navbar navbottom">\n    <li><a href="https://github.com/MFranceschi6">Matteo Franceschi</a></li>\n    <li><a href="https://github.com/edoBaldini">Edoardo Baldini</a></li>\n    <li><a href="https://github.com/Albertomac">Alberto Ottimo</a></li>\n    <li><a href="https://github.com/deselmo">William Guglielmo</a></li>\n    <li><a href="https://github.com/DanyEle">Daniele Gadler</a></li>\n    <li><a href="https://github.com/lorenz944">Lorenzo Casalini</a></li>\n    <li><a href="https://github.com/SuperNabla95">Francesco Tosoni</a></li>\n    <li><a href="https://github.com/Polletz">Riccardo Paoletti</a></li>\n    <li><a class="float-right" href="https://github.com/MFranceschi6/BeepBeepPrimer">Butter Group S.R.L.</a></li>\n  </ul>\n</body>\n</html>' in rv.data

    #the whole page generation for the second run assigned to the user (i.e: ID = 4)
    rv2 = client.get('runs/4')
    assert b'<html>\n<head>\n  <link rel="stylesheet" href="/static/style.css">\n  <link rel="shortcut icon" href="/static/favicon.ico">\n</head>\n<body>\n  <ul class="navbar">\n    <li><img src="/static/nav_logo.png" class="logo" /></li>\n    <li><a href="/">Home</a></li>\n    \n    \n      <li><a href="/create_challenge">Challenges</a></li>\n      <li><a href="/training_objectives">Training Objectives</a></li>\n      <li><a href="/statistics">Statistics</a></li>\n      <li class="float-right"><a href="/logout">Logout</a></li>\n      \n      \n        <li class="float-right"><a href="/fetch">Fetch new Runs</a></li>\n      \n      \n      <li class="float-right"><a href="/profile">Hi emaill@email.com </a></li>\n    \n    \n  \n  </ul>\n  <section>\n    <div class="bodyContainer">\n      <div class="bodyContent">\n\n  <div class="content">\n    <h1 class="text-center textJeansDark">Bondcliff</h1>\n    <h3 class="text-center textPumpkingDark">Monday 30/04/18 at 12:35</h3>\n    \n    <table>\n      <thead>\n        <tr>\n          \n            <th>Distance (m)</th>\n          \n            <th>AVG Speed (m/s)</th>\n          \n            <th>Elapsed Time (s)</th>\n          \n            <th>Elevation (m)</th>\n          \n          <th>Actions</th>\n        </tr>\n      </thead>\n      <tbody>\n        <tr>\n          \n            <td class="text-center">23676.5</td>\n          \n            <td class="text-center">4.385</td>\n          \n            <td class="text-center">5400.0</td>\n          \n            <td class="text-center">0.0</td>\n          \n            <form action="/create_challenge" method="post">\n              <td class="text-center">\n                 <input type="hidden" name="id_run" value=4 />\n                  <a href="#" onclick="document.forms[0].submit()"> \n                  <img class="icon" src="/static/challenge.png"/>\n                </a>\n              </td>\n            </form> \n        </tr>\n      </tbody>\n    </table>\n  </div>\n\n    </div>\n  </div>\n  </section>\n  <ul class="navbar navbottom">\n    <li><a href="https://github.com/MFranceschi6">Matteo Franceschi</a></li>\n    <li><a href="https://github.com/edoBaldini">Edoardo Baldini</a></li>\n    <li><a href="https://github.com/Albertomac">Alberto Ottimo</a></li>\n    <li><a href="https://github.com/deselmo">William Guglielmo</a></li>\n    <li><a href="https://github.com/DanyEle">Daniele Gadler</a></li>\n    <li><a href="https://github.com/lorenz944">Lorenzo Casalini</a></li>\n    <li><a href="https://github.com/SuperNabla95">Francesco Tosoni</a></li>\n    <li><a href="https://github.com/Polletz">Riccardo Paoletti</a></li>\n    <li><a class="float-right" href="https://github.com/MFranceschi6/BeepBeepPrimer">Butter Group S.R.L.</a></li>\n  </ul>\n</body>\n</html>' in rv2.data




#try to access an invalid run ( that doens't exist yet)
def test_invalid_run_accesses(client, app, db_instance, celery_session_worker):
    rv = client.get('/runs/100')
    assert b'!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>Redirecting...</title>\n<h1>Redirecting...</h1>\n<p>You should be redirected automatically to target URL: <a href="/">/</a>.  If not click the link.' in rv.data


# now check that, after logging out from the first user, you can no longer visualize the runs
# of the first user (like run 1) --> i.e: you get a 404 error if trying to access a run that doesn't belong to you
def test_page_generation_after_logout(client, background_app, db_instance, celery_session_worker):
        test_create_runs(client, background_app, db_instance, celery_session_worker)
        rv = client.get('/runs/1')
        assert b'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n<title>404 Not Found</title>\n<h1>Not Found</h1>\n<p>The requested URL was not found on the server.  If you entered the URL manually please check your spelling and try again.</p>\n' in rv.data