import os
import smtplib
import datetime
from email.utils import make_msgid
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText  # Added
from email.mime.image import MIMEImage
from monolith.database import db, User, Run, REPORT_PERIODICITY
from sqlalchemy import func, or_


_SERVER        = None
_MAIL_TEMPLATE = None
_IMG_LOGO      = None
_IMG_PARAMS    = None
_IMG_GITHUB    = None

_CID_LOGO    = make_msgid()
_CID_PARAMS  = make_msgid()
_CID_GITHUB  = make_msgid()


website_name = os.environ['WEBSITE_NAME']
group_name   = os.environ['GROUP_NAME']
gmail_user   = os.environ['GMAIL_USER']
gmail_pass   = os.environ['GMAIL_PASS']

mail_from    = website_name
mail_subject = 'Go to run Bitch!'


def loadMailTemplate():
    global _MAIL_TEMPLATE

    with open('monolith/static/mail_template.html', 'r') as fp:
        _MAIL_TEMPLATE = fp.read().replace('\n', '')
        fp.close()


def loadMIMEImage(filename):
    img = None
    with open('monolith/static/%s' % filename, 'rb') as fp:
        img = MIMEImage(fp.read())
        fp.close()
    return img


def loadImages():
    global _IMG_LOGO, _IMG_PARAMS, _IMG_GITHUB

    _IMG_LOGO   = loadMIMEImage('logo.png')
    _IMG_PARAMS = loadMIMEImage('params.png')
    _IMG_GITHUB = loadMIMEImage('github.png')

    _IMG_LOGO.add_header('Content-ID', '<{}>'.format(_CID_LOGO))
    _IMG_PARAMS.add_header('Content-ID', '<{}>'.format(_CID_PARAMS))
    _IMG_GITHUB.add_header('Content-ID', '<{}>'.format(_CID_GITHUB))


def create_context():
    global _SERVER

    if _SERVER is None:
        _SERVER = smtplib.SMTP('smtp.gmail.com', 587)
        _SERVER.ehlo()
        _SERVER.starttls()
        _SERVER.login(gmail_user, gmail_pass)
        loadMailTemplate()
        loadImages()


def createContent(user):
    global _MAIL_TEMPLATE
    if not isinstance(user, User) or user is None:
        raise TypeError

    today = datetime.date.today()
    delta = datetime.timedelta(days = 0)

    report_periodicity = user.report_periodicity.code
    
    if report_periodicity == REPORT_PERIODICITY[1][0]:
        delta = datetime.timedelta(days = 1)

    if report_periodicity == REPORT_PERIODICITY[2][0]:
        delta = datetime.timedelta(days = 7)

    if report_periodicity == REPORT_PERIODICITY[3][0]:
        delta = datetime.timedelta(months = 1)
    
    startDate = today - delta
    endDate   = today

    runs = db.session.query(
                            func.sum(Run.distance).label('total_distance'),
                            func.avg(Run.average_speed).label('avg_speed')
                        ).filter( 
                            Run.runner_id  == user.id,
                            Run.start_date >= startDate,
                            Run.start_date <= endDate
                        ).first()

    return _MAIL_TEMPLATE.format(
                            website_name       = website_name,
                            group_name         = group_name,
                            report_periodicity = user.report_periodicity.value,
                            total_distance     = runs.total_distance,
                            avg_speed          = runs.avg_speed,
                            cid_logo           = _CID_LOGO,
                            cid_params         = _CID_PARAMS,
                            cid_github         = _CID_GITHUB
                            )


def sendMail(mail_user, content):
    global _SERVER, _IMG_LOGO, _IMG_PARAMS, _IMG_GITHUB
    create_context()

    msg = MIMEMultipart()

    msg['Subject'] = mail_subject
    msg['From']    = mail_from
    msg['To']      = mail_user
   
    msg.attach(MIMEText(content, 'html'))
    msg.attach(_IMG_LOGO)
    msg.attach(_IMG_PARAMS)
    msg.attach(_IMG_GITHUB)

    try:
        _SERVER.sendmail(msg['From'], msg['To'], msg.as_string())
        print("Email sent to %s" % mail_user)
    except Exception as exception:
        print("Error: %s!\n\n" % exception)


def isFirstDayOfWeek(today = datetime.date.today()):
    return (today.isoweekday() == 1)


def isFirstDayOfMonth(today = datetime.date.today()):
    return (today.day == 1)


def _send_reports():
    create_context()
    print("Sending reports...")

    filters = [User.report_periodicity == REPORT_PERIODICITY[1][0]]

    if isFirstDayOfWeek():
        filters.append(User.report_periodicity == REPORT_PERIODICITY[2][0])
        
    if isFirstDayOfMonth():
        filters.append(User.report_periodicity == REPORT_PERIODICITY[3][0])

    users = db.session.query(User).filter( or_(*filters) )

    for u in users:
        mail_user = u.email
        content   = createContent(u)
        print("Sending email to %s" % mail_user)
        sendMail(mail_user, content)
