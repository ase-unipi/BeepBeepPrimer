from flask_wtf import FlaskForm
import wtforms as f
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['email', 'password']


class UserForm(FlaskForm):
    email = f.StringField('email', validators=[DataRequired()])
    firstname = f.StringField('firstname')
    lastname = f.StringField('lastname')
    password = f.PasswordField('password')
    age = f.IntegerField('age')
    weight = f.FloatField('weight')
    max_hr = f.IntegerField('max_hr')
    rest_hr = f.IntegerField('rest_hr')
    vo2max = f.FloatField('vo2max')

    display = ['email', 'firstname', 'lastname', 'password',
               'age', 'weight', 'max_hr', 'rest_hr', 'vo2max']


class DeleteForm(FlaskForm):
    password = f.PasswordField('password', validators=[DataRequired()])
    display = ['password']

class ObjectiveForm(FlaskForm):
    name = f.StringField('Name', validators=[DataRequired()])
    start_date = f.DateField('Start date', validators=[DataRequired()])
    end_date = f.DateField('End Date', validators=[DataRequired()])
    target_distance = f.FloatField('Target Distance', validators=[DataRequired()])

    display = ['name', 'start_date', 'end_date', 'target_distance']