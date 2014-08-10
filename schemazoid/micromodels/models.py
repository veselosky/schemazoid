import six

from .fields import Field


class MetaModel(type):
    """The metaclass for :class:`~schemazoid.micromodels.Model`.

    The main function of this metaclass
    is to move all of fields into the ``_clsfields`` variable on the class.
    """
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
    """The ``Model`` is the key class of the micromodels framework.
    To begin modeling your data structure, subclass ``Model`` and add
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
        # an edge case, we can't call our own __setattr__ before
        # _instance_fields is initialized, since it calls get_field()
        super(Model, self).__setattr__('_instance_fields', {})
        if args:
            self.update(args[0])
        if kwargs:
            self.update(kwargs)

    # We override __setattr__ so that setting attributes passes through field
    # conversion/validation functions.
    def __setattr__(self, key, value):
        field = self.get_field(key)
        if field:
            super(Model, self).__setattr__(key, field.to_python(value))
        else:
            super(Model, self).__setattr__(key, value)

    @classmethod
    def get_class_field(cls, name):
        """Return the Field instance for the class field of the given name.

        Returns None if there is no Field by that name on the class.
        """
        return cls._clsfields.get(name, None)

    @classmethod
    def get_class_fields(cls):
        """Return a dictionary of Fields on this class, keyed by name."""
        return cls._clsfields

    @classmethod
    def add_class_field(cls, name, field):
        """Extend a class by adding a new field to the class definition."""
        if not isinstance(field, Field):
            msg = "Second argument to add_class_field must be a Field instance"
            raise TypeError(msg)
        cls._clsfields[name] = field

    def get_field(self, name):
        """Return the Field instance for the given name on this object.

        This instance method searches both the instance and the class.
        """
        field = self._instance_fields.get(name, None)
        if not field:
            field = self.__class__.get_class_field(name)
        return field

    def get_all_fields(self):
        """Return a dictionary of all Fields on this instance, keyed by name.

        Includes both class fields and instance fields.
        """
        return dict(self.__class__.get_class_fields(), **self._instance_fields)

    def update(self, *args, **kwargs):
        """As with the :class:`dict` method of the same name, given a
        dictionary or keyword arguments, sets the values of the instance
        attributes corresponding to the key names, overriding any existing
        value.
        """
        data = args[0] if args else {}
        for name in self.get_all_fields():
            if name in kwargs:
                setattr(self, name, kwargs[name])
            elif name in data:
                setattr(self, name, data[name])

    def add_field(self, name, field):
        """Adds an instance field to this Model instance.

        Instance fields allow you to validate and serialize arbitrary
        attributes on a Model instance even if the class does not support them.
        """
        self._instance_fields[name] = field
        if hasattr(self, name):
            # Should raise exception if current value not valid
            setattr(self, name, getattr(self, name))

    def to_dict(self, serial=False):
        """Returns a dictionary representing the data of the instance,
        containing native Python objects which might not be serializable
        (for example, :class:`~datetime.datetime` objects). To obtain a
        serializable dictionary, call the
        :meth:`~schemazoid.micromodels.Model.to_serial` method instead,
        or pass the ``serial`` argument with a True value.

        Note that only attributes declared as Fields will be included in the
        dictionary. Although you may set other attributes on the instance,
        those additional attributes will not be returned.
        """
        if serial:
            return dict(
                (key, self.get_field(key).to_serial(getattr(self, key)))
                for key in self.get_all_fields() if hasattr(self, key))
        else:
            return dict((key, getattr(self, key))
                        for key in self.get_all_fields() if hasattr(self, key))

    # Fields have to_serial, for symmetry models should have it to.
    def to_serial(self):
        """Returns a serializable dictionary representing the data of the
        instance. It should be safe to hand this dictionary as-is to
        :func:`json.dumps`.

        Note that only attributes declared as Fields will be included in the
        dictionary. Although you may set other attributes on the instance,
        those additional attributes will not be returned.
        """
        return self.to_dict(serial=True)
