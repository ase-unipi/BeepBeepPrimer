import wtforms as f
import wtforms.widgets.core as wtcore
from wtforms.validators import ValidationError
import datetime
from monolith.database import db, User

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
                message = field.gettext('Field must not be less than %(other_name)s')

            raise ValidationError(message % d)


class NotLessThenToday(object):
    """
    Compares the value of the field with today's date.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        today = datetime.datetime.now().date()
        if field.data < today:
            message = self.message
            if self.message is None:
                message = field.gettext('Field must not be less than today')

            raise ValidationError(message)


class FloatInput(wtcore.Input):
    """
    A custon input tag for float numbers.
    """
    input_type = 'number'

    def __init__(self, step=None, min_=None, max_=None):
        super(FloatInput, self).__init__()
        self.step = step
        self.min_ = min_
        self.max_ = max_

    def __call__(self, field, **kwargs):
        if self.step:
            kwargs['step'] = self.step
        if self.min_:
            kwargs['min'] = self.min_
        if self.max_:
            kwargs['max'] = self.max_

        return super(FloatInput, self).__call__(field, **kwargs)


class UniqueMailValidator(object):
    """
    Compares the value of the field with today's date.

    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if db.session.query(User).filter(User.email == field.data).first() is not None:
            message = self.message
            if self.message is None:
                message = field.gettext('This email has already been used')

            raise ValidationError(message)
