try:
    import simplejson as json
except ImportError:
    import json

from .fields import BaseField


# TODO Add model-level validation to support cross-field dependencies.
class Model(object):
    """The Model is the main component of micromodels. Model makes it trivial
    to parse data from many sources, including JSON APIs.

    You will probably want to initialize this class using the class methods
    :meth:`from_dict` or :meth:`from_kwargs`. If you want to initialize an
    instance without any data, just call :class:`Model` with no parameters.

    A :class:`Model` uses its field specifications to coerce and validate the
    values of attributes when they are set. First, the model checks if it has
    a field with a name matching the key.

    If there is a matching field, then :meth:`to_python` is called on the field
    with the value.

    If :meth:`to_python` does not raise an exception, then the result of
    :meth:`to_python` is set on the instance, and the method is completed.

    If this fails, a ``TypeError`` or ``ValueError`` is raised.

    If the instance doesn't have a field matching the key, then the key and
    value are just set on the instance like any other assignment in Python.
    """

    # FIXME Use six for metaclass syntax compatible with Python 3.
    class __metaclass__(type):
        '''Creates the metaclass for Model. The main function of this metaclass
        is to move all of fields into the _fields variable on the class.
        '''

        # FIXME Move __init__ to __new__ and inherit fields from base classes.
        # See https://github.com/zbyte64/micromodels and
        # https://github.com/jaimegildesagredo/booby for examples.
        def __init__(cls, name, bases, attrs):
            cls._clsfields = {}
            for key, value in attrs.iteritems():
                if isinstance(value, BaseField):
                    cls._clsfields[key] = value
                    delattr(cls, key)

    def __init__(self):
        super(Model, self).__setattr__('_extra', {})

    # FIXME Remove the "is_json" argument from the "from_dict".
    # JSON is obviously not a dict. Parse it yourself.
    # TODO Add "keymap" argument to "from_dict", a dict mapping the field name
    # to the source key in the provided dict.
    @classmethod
    def from_dict(cls, D, is_json=False):
        '''This constructor for :class:`Model` takes a native Python
        dictionary. Any keys in the dictionary that match the names of fields
        on the model will be set on the instance. Other keys will be ignored.
        '''
        instance = cls()
        instance.set_data(D, is_json=is_json)
        return instance

    # FIXME Constructor "from_kwargs" should just be __init__. Merge them.
    @classmethod
    def from_kwargs(cls, **kwargs):
        '''This constructor for :class:`Model` only takes keywork arguments.
        Each key and value pair that represents a field in the :class:`Model`
        is set on the new :class:`Model` instance.
        '''
        instance = cls()
        instance.set_data(kwargs)
        return instance

    # FIXME Remove the "is_json" argument to "set_data".
    # FIXME Remove the "source" attribute for fields. Limits mapping to a
    # single input. Instead provide separate keymaps for different inputs.
    def set_data(self, data, is_json=False):
        if is_json:
            data = json.loads(data)
        for name, field in self._clsfields.iteritems():
            key = field.source or name
            if key in data:
                setattr(self, name, data.get(key))

    def __setattr__(self, key, value):
        if key in self._fields:
            field = self._fields[key]
            field.populate(value)
            field._related_obj = self
            super(Model, self).__setattr__(key, field.to_python())
        else:
            super(Model, self).__setattr__(key, value)

    @property
    def _fields(self):
        return dict(self._clsfields, **self._extra)

    def add_field(self, key, value, field):
        ''':meth:`add_field` must be used to add a field to an existing
        instance of Model. This method is required so that serialization of the
        data is possible. Data on existing fields (defined in the class) can be
        reassigned without using this method.
        '''
        self._extra[key] = field
        setattr(self, key, value)

    def to_dict(self, serial=False):
        '''Returns a dictionary representing the the data of the instance.
        Native Python objects will still exist in this dictionary (for example,
        a ``datetime`` object will be returned rather than a string)
        unless ``serial`` is set to True.
        '''
        if serial:
            return dict((key, self._fields[key].to_serial(getattr(self, key)))
                        for key in self._fields.keys() if hasattr(self, key))
        else:
            return dict((key, getattr(self, key))
                        for key in self._fields.keys() if hasattr(self, key))

    def to_json(self):
        '''Returns a representation of the model as a JSON string. This method
        relies on the :meth:`~micromodels.Model.to_dict` method.
        '''
        return json.dumps(self.to_dict(serial=True))
