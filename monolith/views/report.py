from flask import Blueprint, render_template, make_response, request, flash
from monolith.forms import MailForm

report = Blueprint('report', __name__)


@report.route('/settingreport')
def settingreport():
    
    form = MailForm()
    if form.validate_on_submit():

        option = request.form['options']
        if option is None:
            flash('Select one category', category='error')
            return make_response(render_template('mail.html', form=form), 400)
    return render_template('mail.html', form=form)
