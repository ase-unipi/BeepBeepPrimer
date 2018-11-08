from flask import Blueprint, render_template, request
from monolith.database import db
from monolith.auth import current_user
from monolith.mail_service import _send_reports


test = Blueprint('test', __name__)


@test.route('/test', methods=['GET'])
def _test():
    send_reports()
    return render_template("test.html")
