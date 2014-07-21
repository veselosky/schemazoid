try:
    import simplejson as json
except ImportError:
    import json
import six

from .fields import BaseField


class MetaModel(type):
    '''Creates the metaclass for Model. The main function of this metaclass
    is to move all of fields into the _fields variable on the class.
    '''
    def __new__(cls, name, bases, attrs):
        fields = {}
        for base in bases[::-1]:
            if hasattr(base, '_clsfields'):
                fields.update(base._clsfields)

        # In py3 items() returns a view rather than a copy, which disallows
        # mutation inside the loop. So we make an explicit copy.
        for name, field in attrs.copy().items():
            if isinstance(field, BaseField):
                fields[name] = attrs.pop(name)

        attrs['_clsfields'] = fields
        return super(MetaModel, cls).__new__(cls, name, bases, attrs)


# TODO Add model-level validation to support cross-field dependencies.
@six.add_metaclass(MetaModel)
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
    def __init__(self, *args, **kwargs):
        super(Model, self).__init__()
        # Since we override __setattr__ to search in _extra, when we set it
        # we call super directly to bypass our implementation.
        super(Model, self).__setattr__('_extra', {})
        if kwargs:
            self.set_data(kwargs)

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

    # FIXME Remove the "is_json" argument to "set_data".
    def set_data(self, data, is_json=False):
        if is_json:
            data = json.loads(data)
        for name, field in six.iteritems(self._clsfields):
            if name in data:
                setattr(self, name, data[name])

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
