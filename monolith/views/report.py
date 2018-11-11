from flask import Blueprint, render_template, request, flash
from flask_login import login_required, current_user
from monolith.forms import MailForm
from monolith.database import db, Report

report = Blueprint('report', __name__)

#In this we specify the setting for the management of the report
@report.route('/settingreport', methods=['GET', 'POST'])
@login_required
def settingreport():
    form = MailForm()
    if request.method == 'POST':
            mail = db.session.query(Report).filter(Report.id_user==current_user.id).first()
            if mail is None:
                new_mail = Report()
                new_mail.set_user(current_user.id)
                new_mail.set_timestamp()
                option = request.form['setting_mail']
                new_mail.set_decision(option)
                db.session.add(new_mail)
                db.session.commit()
                flash('Settings updated', category='success')
            else:
                mail.set_timestamp()
                option = request.form['setting_mail']
                mail.set_decision(option)
                db.session.merge(mail)
                db.session.commit()
                flash('Settings updated', category='success')
    return render_template('mail.html', form=form)