from flask_wtf import FlaskForm
import wtforms as f
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class RemoveUserForm(FlaskForm):
    # email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    # display = ['email', 'password']
    display = ['password']


class UserForm(FlaskForm):
    email     = f.StringField('Email', validators=[DataRequired()])
    firstname = f.StringField('Firstname')
    lastname  = f.StringField('Lastname')
    password  = f.PasswordField('Password')
    age       = f.IntegerField('Age')
    weight    = f.FloatField('Weight')
    max_hr    = f.IntegerField('Max Heartrate')
    rest_hr   = f.IntegerField('Rest Heartrate')
    vo2max    = f.FloatField('VO2 Max')

    display = ['email',
               'firstname',
               'lastname',
               'password',
               'age',
               'weight',
               'max_hr',
               'rest_hr',
               'vo2max']
