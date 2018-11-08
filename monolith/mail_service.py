import os
import smtplib
from email.message import EmailMessage
from monolith.database import db, User, REPORT_PERIODICITY
import datetime
from sqlalchemy import or_

_SERVER = None

gmail_user = os.environ['GMAIL_USER']
gmail_pass = os.environ['GMAIL_PASS']

mail_from    = 'BeepBeep Report'
mail_subject = 'Go to run Bitch!'

def create_context():
    global _SERVER

    if _SERVER is None:
        _SERVER = smtplib.SMTP('smtp.gmail.com', 587)
        _SERVER.ehlo()
        _SERVER.starttls()
        _SERVER.login(gmail_user, gmail_pass)

def createContent(user):
    if not isinstance(user, User):
        raise TypeError
    return "You are fucking FANTASTIC :D"

def sendMail(mail_user, content):
    global _SERVER

    create_context()

    msg = EmailMessage()
    msg['Subject'] = mail_subject
    msg['From']    = mail_from
    msg['To']      = mail_user
    msg.set_content(content)

    try:
        _SERVER.send_message(msg)
        print("Email sent to %s" % mail_user)
    except Exception as exception:
        print("Error: %s!\n\n" % exception)


def isLastDayOfWeek(today = datetime.date.today()):
    return (today.isoweekday() == 7);

def isLastDayOfMonth(today = datetime.date.today()):
    day   = 1
    month = today.month + 1
    year  = today.year
    if month > 12:
        month = 1
        year = year + 1
    lastDay = datetime.date(year, month, day) - datetime.timedelta(days = 1)
    return today.day == lastDay.day

def _send_reports():
    print("Sending reports...")

    filters = [User.report_periodicity == REPORT_PERIODICITY[1][0]]

    if isLastDayOfWeek():
        filters.append(User.report_periodicity == REPORT_PERIODICITY[2][0])
        
    if isLastDayOfMonth():
        filters.append(User.report_periodicity == REPORT_PERIODICITY[3][0])

    users = db.session.query(User).filter( or_(*filters) )

    for u in users:
        mail_user = u.email
        content   = createContent(u)
        print("Sending email to %s" % mail_user)
        sendMail(mail_user, content)
