from flask import Blueprint, render_template


errors = Blueprint('errors',__name__)


def page_not_found(e):
    return render_template("error.html", error_name='Page Not Found',
                           error_message='Sorry we can\'t find what you are looking for',
                           redirection='/', redirection_message='run somewhere nice'), 404