from flask import Blueprint, render_template, request
from monolith.database import db
from monolith.auth import current_user, admin_required
from monolith.mail_service import MailService


__mail_service = None

def loadMailService():
    global __mail_service
    if __mail_service is None:
        __mail_service = MailService()


test = Blueprint('test', __name__)


@test.route('/test', methods=['GET'])
@admin_required
def _test():
    global __mail_service
    loadMailService()
    __mail_service.sendReports()
    return render_template("test.html")
