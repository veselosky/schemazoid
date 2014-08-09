import datetime
import six

from dateutil.parser import parse as parse_datetime


# * Django fields contain no instance data, only validation.
# * Django fields contain a reference to their model and their own name within
#   the model.
# * Django fields use a contribute_to_class method to install themselves in a
#   model and set their model and name attributes.

# TODO Add validators to Field to lessen need to sublcass.
# TODO Add required and null validators as keyword args.
# TODO Implement a NotSet value to distinguish between a NULL value that
#      should be serialized and a field that should not be serialized.
class Field(object):
    """Base class for all field types.
    """
    def __init__(self, *args, **kwargs):
        pass

    def to_python(self, data):
        '''This method casts the source data into a
        Python object. The default behavior is to simply return the source
        value. Subclasses should override this method.
        '''
        return data

    def to_serial(self, data):
        '''Used to serialize forms back into JSON or other formats.

        This method is essentially the opposite of
        :meth:`~micromodels.fields.Field.to_python`. A string, boolean,
        number, dictionary, list, or tuple must be returned. Subclasses should
        override this method.

        '''
        return data


class CharField(Field):
    """Field to represent a simple Unicode string value."""

    def to_python(self, data):
        if data is None:
            return six.u('')
        elif hasattr(data, 'isoformat'):
            return data.isoformat()
        return str(data) + six.u('')  # probably dangerous


class IntegerField(Field):
    """Field to represent an integer value"""

    def to_python(self, data):
        if data is None:
            return 0
        return int(data)


class FloatField(Field):
    """Field to represent a floating point value"""

    def to_python(self, data):
        if data is None:
            return 0.0
        return float(data)


class BooleanField(Field):
    """Field to represent a boolean.

    BooleanField uses Python's boolean rules for non-boolean values,
    with one exception: a string containing "false" (case insensitive)
    or "0" will evaluate False."""

    def to_python(self, data):
        if isinstance(data, six.string_types):
            norm = data.strip().lower()
            if norm == 'false' or norm == '0':
                return False
        return bool(data)


class DateTimeField(Field):
    """Field to represent a datetime

    The ``format`` parameter dictates the format of the input strings, and is
    used in the construction of the :class:`datetime.datetime` object.

    The ``serial_format`` parameter is a strftime formatted string for
    serialization. If ``serial_format`` isn't specified, an ISO formatted
    string will be returned by :meth:`~micromodels.DateTimeField.to_serial`.

    """
    def __init__(self, format=None, serial_format=None, **kwargs):
        super(DateTimeField, self).__init__(**kwargs)
        self.format = format
        self.serial_format = serial_format

    def to_python(self, data):
        if data is None:
            return None

        # don't parse data that is already native
        if isinstance(data, datetime.datetime):
            return data
        elif self.format is None:
            # parse as iso8601
            return parse_datetime(data)
        else:
            return datetime.datetime.strptime(data, self.format)

    def to_serial(self, time_obj):
        if not self.serial_format:
            return time_obj.isoformat()
        return time_obj.strftime(self.serial_format)


class DateField(DateTimeField):
    """Field to represent a :mod:`datetime.date`"""

    def to_python(self, data):
        # don't parse data that is already native
        if isinstance(data, datetime.date) or data is None:
            return data

        dt = super(DateField, self).to_python(data)
        return dt.date()


class TimeField(DateTimeField):
    """Field to represent a :mod:`datetime.time`"""

    def to_python(self, data):
        # don't parse data that is already native
        if isinstance(data, datetime.time):
            return data
        elif isinstance(data, datetime.datetime):
            return data.time()
        elif data is None:
            return data
        elif self.format is None:
            # If there are no time delimeters, dateutil misconstrues numbers
            # as the date rather than the time. To ensure it is interpretted
            # as a time, place a parseable date in front of it.
            # See TimeFieldTestCase.test_iso8601_without_delimiters
            today = datetime.datetime.now().date().isoformat()
            return parse_datetime(today + ' at ' + data).time()
        else:
            return datetime.datetime.strptime(data, self.format).time()
