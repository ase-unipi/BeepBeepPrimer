from flask_wtf import FlaskForm
import wtforms as f
import monolith.form_custom_models as fc
from wtforms.validators import DataRequired, NumberRange, Email
from monolith.form_custom_models import UniqueMailValidator
from wtforms.fields.html5 import EmailField


class LoginForm(FlaskForm):
    email    = EmailField('Email', validators=[DataRequired(),
                                               Email()])
    password = f.PasswordField('Password', validators=[DataRequired()])
    
    display  = ['email',
                'password']


class RemoveUserForm(FlaskForm):
    password = f.PasswordField('Password', validators=[DataRequired()])
    
    display  = ['password']


class UserForm(FlaskForm):
    email     = EmailField('Email', validators=[DataRequired(),
                                                Email(),
                                                UniqueMailValidator()])
    firstname = f.StringField('Firstname',       validators=[DataRequired()])
    lastname  = f.StringField('Lastname',        validators=[DataRequired()])
    password  = f.PasswordField('Password',      validators=[DataRequired()])
    age       = f.IntegerField('Age',            validators=[DataRequired()])
    weight    = f.FloatField('Weight',           validators=[DataRequired()])
    max_hr    = f.IntegerField('Max Heartrate',  validators=[DataRequired()])
    rest_hr   = f.IntegerField('Rest Heartrate', validators=[DataRequired()])
    vo2max    = f.FloatField('VO2 Max',          validators=[DataRequired()])

    display = ['email',
               'firstname',
               'lastname',
               'password',
               'age',
               'weight',
               'max_hr',
               'rest_hr',
               'vo2max']


class ProfileForm(UserForm):
  def __init__(self, **kwargs):
        UserForm.__init__(self, **kwargs)
        self['email'].validators = [DataRequired()]
        self['password'].validators = []
        self['password'].flags.required = False
        
   
class TrainingObjectiveSetterForm(FlaskForm):
    start_date = f.DateField('Start date',
                             validators=[DataRequired(message='Not a valid date'), 
                                         fc.NotLessThenToday()],
                             widget=f.widgets.Input(input_type="date"))
    end_date = f.DateField('End date',
                           validators=[DataRequired(message='Not a valid date'),
                                       fc.NotLessThan('start_date', message='Cannot be before Start date'),
                                       fc.NotLessThenToday()],
                           widget=f.widgets.Input(input_type="date"))
    kilometers_to_run = f.FloatField('Kilometers to run',
                                     validators=[DataRequired('You need at least a meter to run'),
                                                 NumberRange(min=0.001, message='You need at least a meter to run')],
                                     widget=fc.FloatInput(step='any', min_='0'),
                                     filters=[lambda value: float('%.3f' % float(value)) if value is not None else value])

    display = ['start_date',
               'end_date',
               'kilometers_to_run']


class TrainingObjectiveVisualizerForm(FlaskForm):
    start_date  = f.DateField('Start')
    end_date    = f.DateField('End')
    kilometers_to_run   = f.FloatField('Km to Run')
    traveled_kilometers = f.FloatField('Traveled Km')
    status              = f.StringField('Status')
    description         = f.StringField('Description')

    display = ['start_date',
               'end_date',
               'kilometers_to_run',
               'traveled_kilometers', 
               'status',
               'description']
