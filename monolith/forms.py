from flask_wtf import FlaskForm
import wtforms as f
import wtforms.widgets.core as wtcore
from wtforms.validators import DataRequired, NumberRange, ValidationError
from wtforms_components import DateRange

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


class MyValidator():
    def validity_check(self, field, limit):
        if len(field.data) < limit:
            raise ValidationError('Date must be at least : ' + limit)


class FloatInput(wtcore.Input):
    """
    A custon input tag for float numbers.
    """
    def __call__(self, field, **kwargs):
        return wtcore.HTMLString('<input %s>' % self.html_params(name=field.name, id=field.id, type="number", step="0.1", min="0", value="1"))


class TrainingObjectiveForm(FlaskForm):
    start_date = f.DateField('Start date',
                             validators=[DataRequired(message='Not a valid date format')],
                             widget = f.widgets.Input(input_type="date"))
    end_date = f.DateField('End date',
                           validators=[DataRequired(message='Not a valid date format')],
                           widget = f.widgets.Input(input_type="date"))
    kilometers_to_run = f.FloatField('Kilometers to run',
                                     validators=[
                                        DataRequired(),
                                        NumberRange(min=0.001, message='You need at least a meter to run')],
                                     widget=FloatInput())

    display = ['start_date', 'end_date', 'kilometers_to_run']
