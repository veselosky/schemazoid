import pytest
import unittest
from datetime import date

from schemazoid import micromodels as m


class ListFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.mixed_list = ['string', 1, 2.1, True, None]
        self.integer_list = [1, 2, 3]
        self.float_list = [1.1, 2.2, 3.3]
        self.date_list = [date(2014, 1, 1), date(2014, 12, 12)]
        self.listfield = m.ListField()

    def test_basic_list(self):
        result = self.listfield.to_python(self.mixed_list)
        self.assertEqual(result, self.mixed_list)

    def test_string_conversion(self):
        """When handed a string value, return a 1-item list containing it."""
        result = self.listfield.to_python('string')
        self.assertEqual(result, ['string'])

    def test_numeric_conversion(self):
        """When handed a numeric value, return a 1-item list containing it."""
        result = self.listfield.to_python(1)
        self.assertEqual(result, [1])

    def test_set_conversion(self):
        """When handed an iterable non-list, return a list."""
        result = self.listfield.to_python(set([1, 2, 3]))
        self.assertEqual(result, [1, 2, 3])

    def test_object_conversion(self):
        thing = object()
        result = self.listfield.to_python(thing)
        self.assertEqual(result, [thing])

    def test_dict_conversion(self):
        """When handed a dict, treat it as an object."""
        mydict = {1: 'one', 2: 'two'}
        result = self.listfield.to_python(mydict)
        self.assertEqual(result, [mydict])

    def test_none_conversion(self):
        """When handed None, return an empty list."""
        self.assertEqual(self.listfield.to_python(None), [])

    def test_to_serial(self):
        self.assertEqual(self.listfield.to_serial(self.mixed_list),
                         self.mixed_list)

    def test_constrained_type_conversion(self):
        field = m.ListField(of_type=m.IntegerField())
        self.assertEqual(field.to_python(self.float_list), self.integer_list)

    def test_constrained_type_to_serial(self):
        field = m.ListField(of_type=m.DateField())
        expected = ['2014-01-01', '2014-12-12']
        self.assertEqual(field.to_serial(self.date_list), expected)

    def test_constrained_type_mutability(self):
        field = m.ListField(of_type=m.DateField())
        result = field.to_python(['2014-01-01', '2014-12-12'])
        result.append('2014-06-06')
        expected = [date(2014, 1, 1), date(2014, 12, 12), date(2014, 6, 6)]
        self.assertEqual(result, expected)


class DictFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.dictfield = m.DictField()

    def test_dict_conversion(self):
        mydict = {1: 'one', 2: 'two'}
        self.assertEqual(self.dictfield.to_python(mydict), mydict)

    def test_none_conversion(self):
        self.assertEqual(self.dictfield.to_python(None), {})

    def test_list_conversion(self):
        self.assertRaises(TypeError, self.dictfield.to_python, [1, 2, 3, 4])

    def test_string_conversion(self):
        self.assertRaises(ValueError, self.dictfield.to_python,
                          "You can't dict a string!")


class ModelFieldTestCase(unittest.TestCase):

    def setUp(self):
        class Person(m.Model):
            name = m.CharField()
            uri = m.CharField()
            email = m.CharField()

        self.Person = Person
        self.data = {
            'name': 'Richard P. Feynman',
            'uri': 'http://en.wikipedia.org/wiki/Richard_Feynman'
        }

    def test_model_field_conversion(self):
        field = m.ModelField(self.Person)
        person = field.to_python(self.data)
        self.assertTrue(isinstance(person, self.Person))
        self.assertEqual(person.name, self.data['name'])
        self.assertEqual(person.uri, self.data['uri'])
        self.assertFalse(hasattr(person, 'email'))

    def test_model_field_to_serial(self):
        field = m.ModelField(self.Person)
        person = field.to_python(self.data)
        self.assertEqual(person.to_serial(), self.data)

    @pytest.mark.skipif(True, reason="TODO")
    def test_failing_modelfield(self):
        """TODO Test when model in the field fails validation"""
        pass
