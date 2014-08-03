from .basic import BaseField


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
