import six

from .fields import Field


class MetaModel(type):
    '''Creates the metaclass for Model. The main function of this metaclass
    is to move all of fields into the _fields variable on the class.
    '''
    def __new__(cls, name, bases, attrs):
        fields = {}
        for base in bases[::-1]:
            if hasattr(base, '_clsfields'):
                fields.update(base._clsfields)

        # Somehow if you iterate over attrs before creating the class, the
        # class docstring gets lost. So we create the class first and
        # manipulate its attrs after.
        newclass = super(MetaModel, cls).__new__(cls, name, bases, attrs)

        to_remove = []
        for name in dir(newclass):
            if isinstance(getattr(newclass, name), Field):
                fields[name] = getattr(newclass, name)
                to_remove.append(name)

        for name in to_remove:
            delattr(newclass, name)

        newclass._clsfields = fields
        return newclass


# TODO Add model-level validation to support cross-field dependencies.
@six.add_metaclass(MetaModel)
class Model(object):
    """The `Model` is the key class of the micromodels framework.
    To begin modeling your data structure, subclass `Model` and add
    Fields describing its structure. ::

        >>> from schemazoid import micromodels as m
        >>> class Thing(m.Model):
        ...   name = m.CharField()
        ...   description = m.CharField()

    A Model instance may be constructed as with any Python object. ::

        >>> thing = Thing()

    More useful and typical is to instatiate a model from a dictionary. ::

        >>> data = {'name': 'spoon', 'description': 'There is no spoon.'}
        >>> thing = Thing(data)
        >>> thing.name
        u'spoon'
        >>> thing.description
        u'There is no spoon.'

        >>> thing.update(name='spork')
        >>> thing.name
        u'spork'
        >>> fork = {'name': 'fork', 'description': "Stick it in me, I'm done."}
        >>> thing.update(fork)
        >>> thing.description
        u"Stick it in me, I'm done."

    """
    def __init__(self, *args, **kwargs):
        super(Model, self).__init__()
        # Since we override __setattr__ to search in _extra, when we set it
        # we call super directly to bypass our implementation.
        super(Model, self).__setattr__('_extra', {})
        if args:
            self.update(args[0])
        if kwargs:
            self.update(kwargs)

    # We override __setattr__ so that setting attributes passes through field
    # conversion/validation functions.
    def __setattr__(self, key, value):
        if key in self._fields:
            field = self._fields[key]
            super(Model, self).__setattr__(key, field.to_python(value))
        else:
            super(Model, self).__setattr__(key, value)

    @property
    def _fields(self):
        return dict(self._clsfields, **self._extra)

    def update(self, *args, **kwargs):
        """As with the `dict` method of the same name, given a dictionary or
        keyword arguments, sets the values of the instance attributes
        corresponding to the key names, overriding any existing value.
        """
        data = args[0] if args else {}
        for name in self._clsfields:
            if name in data:
                setattr(self, name, data[name])
            if name in kwargs:
                setattr(self, name, kwargs[name])

    # Adds fields to instances so that random attrs can be serialized.
    # Undocumenting for now, I'm not sure how I want this to work.
    # -VV 2014-08-04
    def add_field(self, key, value, field):
        self._extra[key] = field
        setattr(self, key, value)

    def to_dict(self, serial=False):
        """Returns a dictionary representing the data of the instance,
        containing native Python objects which might not be serializable
        (for example, :class:`datetime` objects). To obtain a serializable
        dictionary, call the :meth:`to_serial` method instead, or pass
        the `serial` argument with a True value.

        Note that only attributes declared as Fields will be included in the
        dictionary. Although you may set other attributes on the instance,
        those additional attributes will not be returned by :meth:`to_dict`.
        """
        if serial:
            return dict((key, self._fields[key].to_serial(getattr(self, key)))
                        for key in self._fields if hasattr(self, key))
        else:
            return dict((key, getattr(self, key))
                        for key in self._fields if hasattr(self, key))

    # Fields have to_serial, for symmetry models should have it to.
    def to_serial(self):
        """Returns a serializable dictionary representing the data of the
        instance. It should be safe to hand this dictionary as-is to
        `json.dumps`.

        Note that only attributes declared as Fields will be included in the
        dictionary. Although you may set other attributes on the instance,
        those additional attributes will not be returned by :meth:`to_serial`.
        """
        return self.to_dict(serial=True)
