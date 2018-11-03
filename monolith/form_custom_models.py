import wtforms as f
import wtforms.widgets.core as wtcore
from wtforms.validators import ValidationError
import datetime

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
            if self.message is None:
                self.message = field.gettext('Field must not be less than today')

            raise ValidationError(self.message)


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