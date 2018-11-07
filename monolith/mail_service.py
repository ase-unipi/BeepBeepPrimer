import smtplib
from email.message import EmailMessage
from monolith.database import db


gmail_user = 'beepbeep.buttergroup@gmail.com'
gmail_pass = 'butter_group'

mail_subject = 'Go to run Bitch!'
mail_from    = 'BeepBeep Report'
mail_user    = 'albertoottimo@gmail.com'
mail_content = 'Report'

msg = EmailMessage()
msg['Subject'] = mail_subject
msg['From']    = mail_from
msg['To']      = mail_user
msg.set_content(mail_content)

try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(gmail_user, gmail_pass)
    server.send_message(msg)
    server.quit()
except Exception as exception:
    print("Error: %s!\n\n" % exception)


def delivery_mails():
