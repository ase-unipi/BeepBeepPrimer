from flask_wtf import FlaskForm
import wtforms as f
import wtforms.widgets.core as wtcore
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


class DateField(f.DateField):
    """
    A custom data field witch uses a date as type in an input tag.
    """
    widget = f.widgets.Input(input_type="date")

    def __init__(self, label=None, validators=None, **kwargs):
        super(DateField, self).__init__(label, validators, **kwargs)
        self.format = '%Y-%d-%m'



class FloatInput(wtcore.Input):
    """
    A custon input tag for float numbers.
    """
    def __call__(self, field, **kwargs):
        return wtcore.HTMLString('<input %s>' % self.html_params(name=field.name, id=field.id, type="number", step="0.1", min="0", value="1"))


class FloatField(f.FloatField):
    """
    A custom data field witch uses FloatInput as widget.
    """
    widget = FloatInput()

    def __init__(self, label=None, validators=None, **kwargs):
        super(FloatField, self).__init__(label, validators, **kwargs)
        self.format = format


class TrainingObjectiveForm(FlaskForm):
    start_date = DateField('Start date', validators=[DataRequired(message='Not a valid date format')])
    end_date = DateField('End date', validators=[DataRequired(message='Not a valid date format')])
    kilometers_to_run = FloatField('Kilometers to run', validators=[
        DataRequired(),
        NumberRange(min=0.001, message='You need at least a meter to run')])

    display = ['start_date', 'end_date', 'kilometers_to_run']
