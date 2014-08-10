import six
from collections import MutableSequence
from .basic import Field


class TypedList(MutableSequence):
    def __init__(self, field, *args):
        super(TypedList, self).__init__()
        self._field = field
        self._list = [self._field.to_python(item) for item in list(*args)]

    def __getitem__(self, index):
        return self._list[index]

    def __setitem__(self, index, value):
        self._list[index] = self._field.to_python(value)

    def __delitem__(self, index):
        del self._list[index]

    def __len__(self):
        return len(self._list)

    def insert(self, index, value):
        self._list.insert(index, self._field.to_python(value))

    # not abstract, but comparisons fail if not done
    def __eq__(self, *args):
        return self._list.__eq__(*args)

    def __ne__(self, *args):
        return self._list.__ne__(*args)

    def __le__(self, *args):
        return self._list.__le__(*args)

    def __ge__(self, *args):
        return self._list.__ge__(*args)

    def __lt__(self, *args):
        return self._list.__lt__(*args)

    def __gt__(self, *args):
        return self._list.__gt__(*args)

    def __repr__(self, *args):
        return self._list.__repr__(*args)

    def __str__(self, *args):
        return self._list.__str__(*args)


class ListField(Field):
    """A ListField holds arrays of any type.

    Given a non-iterable scalar
    value, it will convert it to a single-item list, unless the value is None,
    in which case it will return an empty list.

    To constrain the type of values allowed in the list, you may pass the
    ``of_type`` argument giving a :class:`~schemazoid.micromodels.Field`
    instance that will be used to convert and validate the values.

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

    Notice in the above Python 2 example, the strings in the ListField are not
    upgraded to unicode. That's a feature of CharField. Listfield performs no
    data conversion. If you want items in the list to be converted, then use
    the ``of_type`` argument.

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
        self._itemfield = Field()
        if isinstance(of_type, Field):
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
            return TypedList(self._itemfield, result)
        return result

    def to_serial(self, items):
        return [self._itemfield.to_serial(item) for item in items]


class DictField(Field):
    """DictField only accepts values that are dictionaries.

    Anything that `dict` can't deal with will raise an exception. DictField
    performs no conversion on the keys or values within the dictionary, which
    can lead to problems during serialization. Make sure any dictionary you
    use contains only simple types for its keys and values.

    If your dictionary has complex types that need processing, use a
    :class:`~schemazoid.micromodels.ModelField` instead.
    """

    def to_python(self, data):
        if data is None:
            return {}
        return dict(data)


class ModelField(Field):
    """Field containing a model instance.

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
    def __init__(self, wrapped_class, **kwargs):
        self._wrapped_class = wrapped_class
        super(ModelField, self).__init__(**kwargs)

    def to_python(self, data):
        if isinstance(data, self._wrapped_class) or data is None:
            return data
        else:
            return self._wrapped_class(data)

    def to_serial(self, model_instance):
        return model_instance.to_serial()
