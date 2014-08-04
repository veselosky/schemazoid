.. schemazoid documentation master file, created by
   sphinx-quickstart on Mon Jul  4 07:57:25 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

schemazoid documentation
======================================
The Model is the main component of micromodels. Its goal is to simplify
the process of modeling data structures, such as dictionaries from a JSON
API, into full Python objects. It also assists with the reverse
transformation, converting itself to a JSON-serializable dictionary.

A :class:`Model` uses its field specifications to define its structure and
validation rules. When you set values for attributes defined as `Field`s,
the value passes through the Field's converstion function before being set
on the model. The value will be coerced to the proper type if possible. If
the value cannot be coerced, the Field will raise a ``TypeError`` or
``ValueError``.

Contents:

.. toctree::
   :maxdepth: 2

   Micromodels API <api>

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

