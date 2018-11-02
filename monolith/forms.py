from flask_wtf import FlaskForm
import wtforms as f
import wtforms.widgets.core as wtcore
from wtforms.validators import DataRequired, NumberRange, ValidationError

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


class NotLessThan(object):
    """
    Compares the values of two fields.

    :param fieldname:
        The name of the other field to compare to.
    :param message:
        Error message to raise in case of a validation error. Can be
        interpolated with `%(other_label)s` and `%(other_name)s` to provide a
        more helpful error.
    """
    def __init__(self, fieldname, message=None):
        self.fieldname = fieldname
        self.message = message

    def __call__(self, form, field):
        try:
            other = form[self.fieldname]
        except KeyError:
            raise ValidationError(field.gettext("Invalid field name '%s'.") % self.fieldname)
        if field.data < other.data:
            d = {
                'other_label': hasattr(other, 'label') and other.label.text or self.fieldname,
                'other_name': self.fieldname
            }
            message = self.message
            if message is None:
                message = field.gettext('Field must not be less than %(other_name)s.')

            raise ValidationError(message % d)


class FloatInput(wtcore.Input):
    """
    A custon input tag for float numbers.
    """
    def __call__(self, field, **kwargs):
        return wtcore.HTMLString('<input %s>' % self.html_params(
            name=field.name,
            id=field.id,
            type="number",
            step="any",
            min="0",
            value="1"))


class TrainingObjectiveForm(FlaskForm):
    start_date = f.DateField('Start date',
                             validators=[DataRequired(message='Not a valid date format')],
                             widget=f.widgets.Input(input_type="date"))
    end_date = f.DateField('End date',
                           validators=[DataRequired(message='Not a valid date format'),
                                       NotLessThan('start_date')],
                           widget=f.widgets.Input(input_type="date"))
    kilometers_to_run = f.FloatField('Kilometers to run',
                                     validators=[DataRequired('You need at least a meter to run'),
                                                 NumberRange(min=0.001, message='You need at least a meter to run')],
                                     widget=FloatInput())

    display = ['start_date', 'end_date', 'kilometers_to_run']
