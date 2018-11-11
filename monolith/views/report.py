from flask import Blueprint, render_template, make_response, request, flash
from flask_login import login_required, current_user
from monolith.forms import MailForm
from monolith.database import db, Report

report = Blueprint('report', __name__)


@report.route('/settingreport', methods=['GET', 'POST'])
@login_required
def settingreport():

    form = MailForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            mail = db.session.query(Report).filter(Report.id_user==current_user.id).first()
            if mail is None:
                new_mail = Report()
                new_mail.set_user(current_user.id)
                new_mail.set_timestamp()
                option = request.form['setting_mail']
                if option is None:
                    flash('Select one category', category='error')
                    return make_response(render_template('mail.html', form=form), 401)
                else:
                    new_mail.set_decision(option)
                    db.session.add(new_mail)
                    #print(new_mail)
                    #print(new_mail.id_user)
                    #print(new_mail.timestamp)
                    #print(new_mail.choice_time)
                    db.session.commit()
                    flash('Settings updated', category='success')
            else:
                mail.set_timestamp()
                option = request.form['setting_mail']
                if option is None:
                    flash('Select one category', category='error')
                    return make_response(render_template('mail.html', form=form), 401)
                else:
                    mail.set_decision(option)
                    db.session.merge(mail)
                    #print(mail)
                    #print(mail.id_user)
                    #print(mail.timestamp)
                    #print(mail.choice_time)
                    db.session.commit()
                    flash('Settings updated', category='success')
    return render_template('mail.html', form=form)