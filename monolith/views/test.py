from flask import Blueprint, render_template, request
from monolith.database import db
from monolith.auth import current_user


test = Blueprint('test', __name__)


@test.route('/test', methods=['GET'])
def _test():
    return render_template("test.html")
