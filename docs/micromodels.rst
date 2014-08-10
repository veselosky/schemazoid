Micromodels
===================

A :class:`~schemazoid.micromodels.Model` uses its field specifications to define
its structure and validation rules. When you set a value for an attribute defined
as a :class:`~schemazoid.micromodels.Field`, the value passes through the Field's
conversion function before being set on the model. The value will be coerced to
the proper type if possible. If the value cannot be coerced, the Field will
raise a ``TypeError`` or ``ValueError``.

Models
-------------------

.. autoclass:: schemazoid.micromodels.Model
    :members:

Fields
-------------------

.. autoclass:: schemazoid.micromodels.Field
    :members:

Basic Fields
~~~~~~~~~~~~~~~~~~

.. autoclass:: schemazoid.micromodels.BooleanField
.. autoclass:: schemazoid.micromodels.CharField
.. autoclass:: schemazoid.micromodels.IntegerField
.. autoclass:: schemazoid.micromodels.FloatField

Datetime Fields
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: schemazoid.micromodels.DateTimeField
.. autoclass:: schemazoid.micromodels.DateField
.. autoclass:: schemazoid.micromodels.TimeField

Complex Fields
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: schemazoid.micromodels.ListField
.. autoclass:: schemazoid.micromodels.DictField
.. autoclass:: schemazoid.micromodels.ModelField
