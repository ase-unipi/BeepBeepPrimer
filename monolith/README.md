# monolith
Define a set of files on the base of the application

:open_file_folder: templates: contains the HTML of the views.  
    At the moments includes only pages related to the login and the home page.

- [app.py](app.py) contains the main and the `create_app` function that initialize the database, the environment and the Flask app.
- [auth.py](auth.py) contains:
    - `admin_required(func)`
    - `fetch_runs(user)`
- [background.py](background.py) defines task that runs in background.
    - `fetch_all_runs()` all runs of all users
    - `fetch_runs(user)` all runs of a specific user
    - `activity2run(user, activity)` used by `fetch_runs(user)` to convert a strava run into a DB entry
- [database.py](database.py) manage the database using SQLAlchemy.  
  It contains two classes:
    - User
    - Run
- [forms.py](forms.py) defines the LoginForm and the UserForm
