from datetime import datetime, timedelta

from flask_mail import Mail, Message

from monolith.background import celery
from monolith.database import db, User, Run

_APP = None


@celery.task
def send_all_mail():
    global _APP
    # lazy init
    if _APP is None:
        from monolith.app import create_app
        app = create_app()
        db.init_app(app)
    else:
        app = _APP
    mail = Mail(app)

    users = db.session.query(User).filter()
    for user in users:
        body = prepare_body(user)
        if body:
            msg = Message('Your BeepBeep Report', sender=app.config['MAIL_USERNAME'], recipients=[user.email])
            msg.body = body
            mail.send(msg)


def prepare_body(user):
    body = ""
    runs = db.session.query(Run).filter(Run.runner == user, Run.start_date >= (datetime.now() - timedelta(days=15)))
    if runs.count() == 0:
        return None
    for run in runs:
        body += "name: " + run.name + "\n"
    return body
