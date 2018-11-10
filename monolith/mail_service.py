import os
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import make_msgid
from monolith.database import db, User, Run, ReportPeriodicity
from sqlalchemy import func, or_

class MailService:

    def __init__(self):
        
        # Server config
        self.__website        = os.environ['WEBSITE_NAME']
        self.__group          = os.environ['GROUP_NAME']
        self.__mail_subject   = os.environ['MAIL_REPORT_SUBJECT']
        self.__message_no_run = os.environ['MAIL_MESSAGE_NO_RUN']
        
        # SMTP Server
        gmail_user = os.environ['MAIL_GMAIL_USER']
        gmail_pass = os.environ['MAIL_GMAIL_PASS']
        self.__server = smtplib.SMTP('smtp.gmail.com', 587)
        self.__server.ehlo()
        self.__server.starttls()
        self.__server.login(gmail_user, gmail_pass)

        
        self.__base_folder = 'monolith/static/mail'
        
        # Templates
        self.__content       = 'content_template.html'
        self.__report_no_run = 'report_no_run_template.html'
        self.__report_run    = 'report_run_template.html'
        templates_filenames  = [self.__content,
                                self.__report_no_run,
                                self.__report_run]
        self.__templates     = dict.fromkeys(templates_filenames)
        
        # Images
        self.__logo       = '_logo.png'
        self.__params     = '_params.png'
        self.__github     = '_github.png'
        images_filenames  = [self.__logo,
                             self.__params,
                             self.__github]
        self.__images     = dict.fromkeys(images_filenames)                    
        self.__images_CID = dict.fromkeys(images_filenames)

        self.__loadTemplates()
        self.__loadImages()
        self.__updateToday()


    def __loadFile(self, filename, flags):
        with open(self.__base_folder + '/' + filename, flags) as f:
            data = f.read()
            f.close()
        return data        


    def __loadTemplates(self):
        for filename in self.__templates.keys():
            self.__templates[filename] = self.__loadFile(filename, 'r').replace('\n', '')


    def __loadMIMEImage(self, filename):
        imageData = self.__loadFile(filename, 'rb')
        imageCID  = make_msgid()[1:-1]
        imageMIME = MIMEImage(imageData, 'png')
        imageMIME.add_header('Content-ID', '<{}>'.format(imageCID))
        imageMIME.add_header('Content-Disposition', 'inline', filename = filename)
            
        return imageMIME, imageCID


    def __loadImages(self):
        for filename in self.__images.keys():
            self.__images[filename], self.__images_CID[filename] = self.__loadMIMEImage(filename)


    # TODO: refactoring
    def __getDeltaFromPeriodicity(self, periodicity):

        delta = datetime.timedelta(seconds = 0)

        if periodicity   == ReportPeriodicity.daily:
            delta = datetime.timedelta(days = 1)
        elif periodicity == ReportPeriodicity.weekly:
            delta = datetime.timedelta(days = 7)
        elif periodicity == ReportPeriodicity.monthly:
            delta = datetime.timedelta(months = 1)
        
        return delta


    def __getUserReportResult(self, user):
        report_periodicity = user.report_periodicity

        delta     = self.__getDeltaFromPeriodicity(report_periodicity)
        endDate   = self.__today
        startDate = endDate - delta
        
        result = db.session.query(
                                func.sum(Run.distance).label('total_distance'),
                                func.avg(Run.average_speed).label('avg_speed')
                            ).filter( 
                                Run.runner_id  == user.id,
                                Run.start_date >= startDate,
                                Run.start_date <= endDate
                            ).first()
        return result


    def __createMIMEContent(self, user):
        result = self.__getUserReportResult(user)

        if result.total_distance is None:
            template = self.__templates[self.__report_no_run]
            result_content = template.format(
                                        message = self.__message_no_run
                                        )
        else:
            template = self.__templates[self.__report_run]
            result_content = template.format(
                                        total_distance = result.total_distance,
                                        avg_speed      = result.avg_speed
                                        )

        template = self.__templates[self.__content]
        content = template.format(
                            website     = self.__website,
                            group       = self.__group,
                            periodicity = user.report_periodicity.name,
                            result      = result_content,
                            cid_logo    = self.__images_CID[self.__logo],
                            cid_params  = self.__images_CID[self.__params],
                            cid_github  = self.__images_CID[self.__github]
                            )
        return MIMEText(content, 'html')


    def __sendMail(self, user):
        msg = MIMEMultipart('related')

        msg['Subject'] = self.__mail_subject
        msg['From']    = self.__website
        msg['To']      = user.email
       
        contentMIME = self.__createMIMEContent(user)
        msg.attach(contentMIME)

        for imageMIME in self.__images.values():
            msg.attach(imageMIME)

        try:
            self.__server.sendmail(
                            msg['From'],
                            msg['To'],
                            msg.as_string()
                            )
            print("Email sent to %s" % msg['To'])
        except Exception as exception:  
            print("Error: %s!\n\n" % exception)


    def __updateToday(self):
        self.__today = datetime.datetime.today().replace(hour = 0, minute = 0, second = 0)


    def sendReports(self):
        print("Sending reports...")

        self.__updateToday()
        # Daily
        filters = [User.report_periodicity == ReportPeriodicity.daily.name]
        # Weekly
        if self.__today.isoweekday() == 1: # First day of the week
            filters.append(User.report_periodicity == ReportPeriodicity.weekly.name)
        # Monthly
        if self.__today.day == 1:          # First day of the month
            filters.append(User.report_periodicity == ReportPeriodicity.montly.name)

        users = db.session.query(User).filter( or_(*filters) )

        for user in users:
            self.__sendMail(user)
