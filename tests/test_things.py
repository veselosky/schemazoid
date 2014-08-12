"""
[ ] TODO Implement and test URLField
[ ] TODO Implement and test OneOf for fields that accept more than one type.
[ ] TODO Attempt auto-generation of models from schema.rdfs.org
http://python-3-patterns-idioms-test.readthedocs.org/en/latest/Metaprogramming.html
"""
# import pytest
import unittest

from schemazoid import things as t
from schemazoid import micromodels as m


class ThingTestCase(unittest.TestCase):

    def test_thing_empty(self):
        thing = t.Thing()
        self.assertTrue(isinstance(thing, m.Model))
