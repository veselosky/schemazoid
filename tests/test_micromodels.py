import unittest
from datetime import datetime
from pytz import utc

from schemazoid import micromodels as m

# TEST Add validators to Field
# TEST Add required and null validation args to Field.
# TEST Implement NotSet value for Field.
# TEST Model-level validation.
# TODO Sort out the related_name question.


class ClassCreationTestCase(unittest.TestCase):

    def setUp(self):
        class SimpleModel(m.Model):
            name = m.CharField()
            other = m.CharField()
        self.model_class = SimpleModel
        self.instance = SimpleModel()

    def test_class_created(self):
        """Model instance should be of type SimpleModel"""
        self.assertTrue(isinstance(self.instance, self.model_class))

    def test_fields_created(self):
        # FIXME This is testing an implementation detail, not a public API.
        self.assertTrue(hasattr(self.instance, '_fields'))

    def test_field_collected(self):
        """Model property should be of correct type"""
        self.assertTrue(isinstance(self.instance._fields['name'], m.CharField))


class ModelConstructorTestCase(unittest.TestCase):

    def setUp(self):
        class Thing(m.Model):
            name = m.CharField()
            description = m.CharField()
        self.Thing = Thing

    def test_kwargs(self):
        """Construct by passing keyword arguments"""
        thing = self.Thing(name="The name", description="The other")
        self.assertTrue(isinstance(thing, self.Thing))
        self.assertEqual(thing.name, 'The name')
        self.assertEqual(thing.description, 'The other')

    def test_args(self):
        """Construct by passing a dictionary"""
        thing = self.Thing({'name': "The name", 'description': "The other"})
        self.assertTrue(isinstance(thing, self.Thing))
        self.assertEqual(thing.name, 'The name')
        self.assertEqual(thing.description, 'The other')

    def test_args_and_kwargs(self):
        """Construct by passing a dictionary AND keyword arguments. Keywords
        should override values in the dictionary.
        """
        thing = self.Thing({'name': "The name", 'description': "The other"},
                           name="A Thing by any other name")
        self.assertTrue(isinstance(thing, self.Thing))
        self.assertEqual(thing.name, 'A Thing by any other name')
        self.assertEqual(thing.description, 'The other')


class InheritenceTestCase(unittest.TestCase):

    def setUp(self):
        class Parent(m.Model):
            name = m.CharField()
            age = m.IntegerField()

        class Child(Parent):
            age = m.FloatField()

        class Grandchild(Child):
            school = m.CharField()

        self.Parent = Parent
        self.Child = Child
        self.Grandchild = Grandchild
        self.data = {'name': 'Eric', 'age': 18, 'school': 'no way dude'}

    def test_child_inherits_parent_fields(self):
        child = self.Child(self.data)
        self.assertEqual(child.name, self.data['name'])

    def test_non_field_keys_ignored(self):
        child = self.Child(self.data)
        self.assertFalse(hasattr(child, 'school'))

    def test_child_overrides_parent_fields(self):
        child = self.Child(self.data)
        self.assertEqual(child.age, 18.0)

    def test_grandchild_field_mro(self):
        grandchild = self.Grandchild(self.data)
        self.assertEqual(grandchild.name, self.data['name'])
        self.assertEqual(grandchild.school, self.data['school'])
        self.assertEqual(grandchild.age, 18.0)


class ModelTestCase(unittest.TestCase):

    def setUp(self):
        self.data = {
            'id': '1',
            'title': 'Title',
            'summary': 'Description of the contents.',
            'updated': '2014-08-09T12:21:00Z',
            'category': ['blogpost', 'test'],
            'author': {'name': 'Richard P. Feynman',
                       'uri': 'http://en.wikipedia.org/wiki/Richard_Feynman'},
        }

        class Atom(m.Model):
            id = m.IntegerField()  # not really, but for testing purposes
            title = m.CharField()
            summary = m.CharField()
            updated = m.DateTimeField()
            category = m.ListField()
            author = m.DictField()

        self.Atom = Atom

    def test_model_creation(self):
        atom = self.Atom(self.data)
        self.assertTrue(isinstance(atom, self.Atom))
        self.assertEqual(atom.title, self.data['title'])
        self.assertEqual(atom.id, 1)
        self.assertTrue(isinstance(atom.updated, datetime))
        self.assertEqual(atom.category, self.data['category'])
        self.assertEqual(atom.author['name'], self.data['author']['name'])

    def test_model_serialization(self):
        atom = self.Atom(self.data)
        serial = atom.to_serial()
        self.assertEqual(serial['id'], 1)
        self.assertEqual(serial['updated'], atom.updated.isoformat())
        self.assertEqual(atom.category, self.data['category'])
        self.assertEqual(atom.author['name'], self.data['author']['name'])

    def test_model_late_assignment(self):
        atom = self.Atom(self.data)
        atom.id = '2'
        self.assertEqual(atom.id, 2)
        atom.updated = '2014-08-09T12:22:00Z'
        self.assertEqual(atom.updated, datetime(2014, 8, 9, 12, 22, 0, 0, utc))
        atom.category.append('physics')
        self.assertEqual(atom.category, ['blogpost', 'test', 'physics'])
        atom.author['email'] = 'richard@feynman.com'
        serial = atom.to_serial()
        self.assertEqual(serial['author'], atom.author)
        self.assertEqual(serial['author']['email'], 'richard@feynman.com')


if __name__ == "__main__":
    unittest.main()
