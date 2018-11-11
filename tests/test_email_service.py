from unittest import mock
from monolith.database import User, Run, ReportPeriodicity
from datetime import date, timedelta
from monolith.background import send_reports
from monolith.mail_service import MailService


def send_fake_mail(self):
    assert 0 == 1


def test_send_mail_called(client, background_app, celery_session_worker, db_instance):
    from monolith import background
    background.__mail_service = mock.MagicMock()
    res = send_reports.delay()
    res.wait()
    assert background.__mail_service.sendReports.called


def test_send_mail_no_user(app, db_instance):
    with app.app_context():
        mailservice = MailService()
        mailservice._MailService__sendMail = mock.MagicMock()
        mailservice.sendReports()
        assert not mailservice._MailService__sendMail.called


def test_send_mail_one_user(app, db_instance):
    u = User(email='email@email.com', firstname='a', lastname='a', password='pass', age=1, weight=1,
             max_hr=1, vo2max=1, report_periodicity=ReportPeriodicity.daily)
    db_instance.session.add(u)
    db_instance.session.commit()
    with app.app_context():
        mailservice = MailService()
        mailservice._MailService__sendMail = mock.MagicMock()
        mailservice.sendReports()
        assert mailservice._MailService__sendMail.called


def test_send_mail_more_user(app, db_instance):
    u = User(email='email@email.com', firstname='a', lastname='a', password='pass', age=1, weight=1,
             max_hr=1, vo2max=1, report_periodicity=ReportPeriodicity.daily)
    db_instance.session.add(u)
    db_instance.session.commit()
    u = User(email='emaill@email.com', firstname='a', lastname='a', password='pass', age=1, weight=1,
             max_hr=1, vo2max=1, report_periodicity=ReportPeriodicity.no)
    db_instance.session.add(u)
    db_instance.session.commit()
    with app.app_context():
        with mock.patch('monolith.mail_service.smtplib.SMTP') as mocked:
            mailservice = MailService()
            mailservice.sendReports()
            assert mocked.return_value.sendmail.call_count == 1


def test_send_mail_no_runs(app, db_instance):
    u = User(email='email@email.com', firstname='a', lastname='a', password='pass', age=1, weight=1,
             max_hr=1, vo2max=1, report_periodicity=ReportPeriodicity.daily)
    db_instance.session.add(u)
    db_instance.session.commit()
    with app.app_context():
        with mock.patch('monolith.mail_service.smtplib.SMTP') as mocked:
            mailservice = MailService()
            mailservice.sendReports()
            print(mocked.return_value.sendmail.call_args[0][2])
            assert "From: Butter BeepBeep" in mocked.return_value.sendmail.call_args[0][2]
            assert "To: email@email.com" in mocked.return_value.sendmail.call_args[0][2]
            assert "You did not run in this period!" in mocked.return_value.sendmail.call_args[0][2]


def test_send_mail_with_runs(app, db_instance):
    u = User(email='email@email.com', firstname='a', lastname='a', password='pass', age=1, weight=1,
             max_hr=1, vo2max=1, report_periodicity=ReportPeriodicity.daily)
    db_instance.session.add(u)
    db_instance.session.commit()
    r = Run(name='run', strava_id=1, distance=1000, start_date=date.today(), average_speed=20.1, elapsed_time=1000 * 60,
            average_heartrate=0, total_elevation_gain=0, runner_id=u.id)
    db_instance.session.add(r)
    db_instance.session.commit()
    with app.app_context():
        with mock.patch('monolith.mail_service.smtplib.SMTP') as mocked:
            mailservice = MailService()
            mailservice.sendReports()
            print(mocked.return_value.sendmail.call_args[0][2])
            assert "From: Butter BeepBeep" in mocked.return_value.sendmail.call_args[0][2]
            assert "To: email@email.com" in mocked.return_value.sendmail.call_args[0][2]
            assert "Total Distance</h2>" in mocked.return_value.sendmail.call_args[0][2]
            assert "1000.0</h3>" in mocked.return_value.sendmail.call_args[0][2]
            assert "Average Speed</h2>" in mocked.return_value.sendmail.call_args[0][2]
            assert "20.1</h3>" in mocked.return_value.sendmail.call_args[0][2]
