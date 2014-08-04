import six
from .basic import BaseField


class ListField(BaseField):
    """A ListField holds arrays of any type.

    Given a non-iterable scalar
    value, it will convert it to a single-item list, unless the value is None,
    in which case it will return an empty list.

    To constrain the type of values allowed in the list, you may pass the
    'of_type' argument giving a Field instance that will be used to convert
    and validate the values.

    Here are some examples::

        >>> from schemazoid import micromodels as m
        >>> class Stooge(m.Model):
        ...   name = m.CharField()
        ...   alternateName = m.ListField()
        ...
        >>> data = {'name':'Shemp', 'alternateName':['Larry', 'Mo', 'Curly']}
        >>> stooge = Stooge(data)
        >>> stooge.name
        u'Shemp'

        >>> stooge.alternateName
        ['Larry', 'Mo', 'Curly']

        >>> stooge.to_dict()
        {'alternateName': ['Larry', 'Mo', 'Curly'], 'name': u'Shemp'}

    Notice in the above Python 2 example, the strings in the ListField are not
    upgraded to unicode. That's a feature of CharField. Listfield performs no
    data conversion. If you want items in the list to be converted, then use
    the of_type argument.

        >>> class Event(m.Model):
        ...     dates = m.ListField(of_type=m.DateField())
        >>> f = Event(dates=['1999-12-31', '2015-12-31'])

        >>> f.dates
        [datetime.date(1999, 12, 31), datetime.date(2015, 12, 31)]

        >>> f.to_dict()
        {'dates': [datetime.date(1999, 12, 31), datetime.date(2015, 12, 31)]}

        >>> f.to_dict(serial=True)
        {'dates': ['1999-12-31', '2015-12-31']}

    In the above example, the DateField is used both to convert and to
    serialize the data items in the list.
    """
    def __init__(self, of_type=None, **kwargs):
        super(ListField, self).__init__(**kwargs)
        self._itemfield = BaseField()
        if isinstance(of_type, BaseField):
            self._itemfield = of_type

    def to_python(self, data):
        # Dictionaries and strings are both iterable, but should not be
        # treated as arrays for this purpose.
        if isinstance(data, dict):
            result = [data]
        elif isinstance(data, six.string_types):
            result = [data]
        elif hasattr(data, '__iter__'):
            result = list(data)
        elif data is None:
            result = []
        else:
            result = [data]

        if self._itemfield:
            return [self._itemfield.to_python(item) for item in result]
        return result

    def to_serial(self, items):
        return [self._itemfield.to_serial(item) for item in items]


class DictField(BaseField):
    """DictField only accepts values that are dictionaries.

    Anything that `dict` can't deal with will raise an exception. DictField
    performs no conversion on the keys or values within the dictionary, which
    can lead to problems during serialization. Make sure any dictionary you
    use contains only simple types for its keys and values.

    If your dictionary has complex types that need processing, use a
    `ModelField` instead.
    """

    def to_python(self, data):
        if data is None:
            return {}
        return dict(data)


class WrappedObjectField(BaseField):
    """Superclass for any fields that wrap an object"""

    def __init__(self, wrapped_class, related_name=None, **kwargs):
        self._wrapped_class = wrapped_class
        self._related_name = related_name

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

        return obj

    def to_serial(self, model_instance):
        return model_instance.to_dict(serial=True)
