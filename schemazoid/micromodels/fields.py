import datetime
import six

from dateutil.parser import parse as parse_datetime


# * Django fields contain no instance data, only validation.
# * Django fields contain a reference to their model and their own name within
#   the model.
# * Django fields use a contribute_to_class method to install themselves in a
#   model and set their model and name attributes.

# TODO Add validators to BaseField to lessen need to sublcass.
# TODO Add required and null validators as keyword args.
# TODO Implement a NotSet value to distinguish between a NULL value that
#      should be serialized and a field that should not be serialized.
class BaseField(object):
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
        :meth:`~micromodels.fields.BaseField.to_python`. A string, boolean,
        number, dictionary, list, or tuple must be returned. Subclasses should
        override this method.

        '''
        return data


class CharField(BaseField):
    """Field to represent a simple Unicode string value."""

    def to_python(self, data):
        if data is None:
            return six.u('')
        return data + six.u('')  # probably dangerous


class IntegerField(BaseField):
    """Field to represent an integer value"""

    def to_python(self, data):
        if data is None:
            return 0
        return int(data)


class FloatField(BaseField):
    """Field to represent a floating point value"""

    def to_python(self, data):
        if data is None:
            return 0.0
        return float(data)


# FIXME Boolean to_python gives unexpected results. Use Django's logic instead.
class BooleanField(BaseField):
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


class DateTimeField(BaseField):
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


class WrappedObjectField(BaseField):
    """Superclass for any fields that wrap an object"""

    def __init__(self, wrapped_class, related_name=None, **kwargs):
        self._wrapped_class = wrapped_class
        self._related_name = related_name
        self._related_obj = None

        BaseField.__init__(self, **kwargs)


class ModelField(WrappedObjectField):
    """Field containing a model instance

    Use this field when you wish to nest one object inside another.
    It takes a single required argument, which is the nested class.
    For example, given the following dictionary::

        >>> some_data = {
        ...     'first_item': 'Some value',
        ...     'second_item': {
        ...         'nested_item': 'Some nested value',
        ...     },
        ... }

    You could build the following classes
    (note that you have to define the inner nested models first)::

        >>> from schemazoid import micromodels
        >>> class MyNestedModel(micromodels.Model):
        ...     nested_item = micromodels.CharField()

        >>> class MyMainModel(micromodels.Model):
        ...     first_item = micromodels.CharField()
        ...     second_item = micromodels.ModelField(MyNestedModel)

    Then you can access the data as follows::

        >>> m = MyMainModel(some_data)
        >>> m.first_item
        u'Some value'
        >>> m.second_item.__class__.__name__
        'MyNestedModel'
        >>> m.second_item.nested_item
        u'Some nested value'

    """
    def to_python(self, data):
        if isinstance(data, self._wrapped_class):
            obj = data
        else:
            obj = self._wrapped_class(data or {})

        # Set the related object to the related field
        if self._related_name is not None:
            setattr(obj, self._related_name, self._related_obj)

        return obj

    def to_serial(self, model_instance):
        return model_instance.to_dict(serial=True)


class ModelCollectionField(WrappedObjectField):
    """Field containing a list of model instances.

    Use this field when your source data dictionary contains a list of
    dictionaries. It takes a single required argument, which is the name of the
    nested class that each item in the list should be converted to.
    For example::

        >>> some_data = {
        ...     'list': [
        ...         {'value': 'First value'},
        ...         {'value': 'Second value'},
        ...         {'value': 'Third value'},
        ...     ]
        ... }

        >>> from schemazoid import micromodels
        >>> class MyNestedModel(micromodels.Model):
        ...     value = micromodels.CharField()

        >>> class MyMainModel(micromodels.Model):
        ...     list = micromodels.ModelCollectionField(MyNestedModel)

        >>> m = MyMainModel(some_data)
        >>> len(m.list)
        3
        >>> m.list[0].__class__.__name__
        'MyNestedModel'
        >>> m.list[0].value
        u'First value'
        >>> [item.value for item in m.list]
        [u'First value', u'Second value', u'Third value']

    """
    def to_python(self, data):
        object_list = []
        for item in data:
            obj = self._wrapped_class(item)
            if self._related_name is not None:
                setattr(obj, self._related_name, self._related_obj)
            object_list.append(obj)

        return object_list

    def to_serial(self, model_instances):
        return [instance.to_dict(serial=True) for instance in model_instances]


class FieldCollectionField(BaseField):
    """Field containing a list of the same type of fields.

    The constructor takes an instance of the field.

    Here are some examples::

        >>> from schemazoid import micromodels as m
        >>> class Thing(m.Model):
        ...   name = m.CharField()
        ...   birthday = m.DateField()
        ...   alternateName = m.FieldCollectionField(m.CharField())
        ...
        >>> data = {'name':'Nobody', 'alternateName':['Larry', 'Mo', 'Curly']}
        >>> thing = Thing(data)
        >>> thing.name
        u'Nobody'
        >>> thing.alternateName
        [u'Larry', u'Mo', u'Curly']
        >>> thing.to_dict()
        {'alternateName': [u'Larry', u'Mo', u'Curly'], 'name': u'Nobody'}
        >>> thing.to_dict(serial=True)
        {'alternateName': [u'Larry', u'Mo', u'Curly'], 'name': u'Nobody'}

        >>> class Event(m.Model):
        ...     dates = m.FieldCollectionField(m.DateField())
        >>> f = Event(dates=['1999-12-31', '2015-12-31'])

        >>> f.dates
        [datetime.date(1999, 12, 31), datetime.date(2015, 12, 31)]

        >>> f.to_dict()
        {'dates': [datetime.date(1999, 12, 31), datetime.date(2015, 12, 31)]}

        >>> f.to_dict(serial=True)
        {'dates': ['1999-12-31', '2015-12-31']}

    """
    def __init__(self, field_instance, **kwargs):
        super(FieldCollectionField, self).__init__(**kwargs)
        self._instance = field_instance

    def to_python(self, data):
        def convert(item):
            return self._instance.to_python(item)
        return [convert(item) for item in data or []]

    def to_serial(self, list_of_fields):
        return [self._instance.to_serial(data) for data in list_of_fields]
