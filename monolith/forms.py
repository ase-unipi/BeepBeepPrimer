from flask_wtf import FlaskForm
import wtforms as f
import form_custom_models as fc
from wtforms.validators import DataRequired, NumberRange

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
    
class TrainingObjectiveForm(FlaskForm):
    start_date = f.DateField('Start date',
                             validators=[DataRequired(message='Not a valid date format'), 
                                         fc.NotLessThenToday()],
                             widget=f.widgets.Input(input_type="date"))
    end_date = f.DateField('End date',
                           validators=[DataRequired(message='Not a valid date format'),
                                       fc.NotLessThan('start_date', message='End date must not be less than Start date'),
                                       fc.NotLessThenToday()],
                           widget=f.widgets.Input(input_type="date"))
    kilometers_to_run = f.FloatField('Kilometers to run',
                                     validators=[DataRequired('You need at least a meter to run'),
                                                 NumberRange(min=0.001, message='You need at least a meter to run')],
                                     widget=fc.FloatInput(step='any', min_='0'),
                                     filters=[lambda value: float('%.3f' % float(value)) if value is not None else value])

    display = ['start_date', 'end_date', 'kilometers_to_run']
