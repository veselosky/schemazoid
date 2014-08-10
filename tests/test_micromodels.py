import unittest
from datetime import datetime
from pytz import utc

from schemazoid import micromodels as m

# TEST Add validators to Field
# TEST Add required and null validation args to Field.
# TEST Implement NotSet value for Field.
# TEST Model-level validation.


class ClassCreationTestCase(unittest.TestCase):

    def setUp(self):
        class SimpleModel(m.Model):
            name = m.CharField()

        self.model_class = SimpleModel
        self.instance = SimpleModel()

    def test_class_created(self):
        self.assertTrue(isinstance(self.instance, self.model_class))

    def test_field_collected(self):
        self.assertTrue(isinstance(self.instance.get_field('name'),
                        m.CharField))


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
        class Person(m.Model):
            name = m.CharField()
            uri = m.CharField()
            email = m.CharField()

        class Atom(m.Model):
            id = m.IntegerField()  # not really, but for testing purposes
            title = m.CharField()
            summary = m.CharField()
            updated = m.DateTimeField()
            category = m.ListField()
            author = m.ModelField(Person)

        self.Person = Person
        self.Atom = Atom
        self.data = {
            'id': '1',
            'title': 'Title',
            'summary': 'Description of the contents.',
            'updated': '2014-08-09T12:21:00Z',
            'category': ['blogpost', 'test'],
            'author': {'name': 'Richard P. Feynman',
                       'uri': 'http://en.wikipedia.org/wiki/Richard_Feynman'},
        }

    def test_model_creation(self):
        atom = self.Atom(self.data)
        self.assertTrue(isinstance(atom, self.Atom))
        self.assertEqual(atom.title, self.data['title'])
        self.assertEqual(atom.id, 1)
        self.assertTrue(isinstance(atom.updated, datetime))
        self.assertEqual(atom.category, self.data['category'])
        self.assertEqual(atom.author.name, self.data['author']['name'])

    def test_model_to_dict(self):
        atom = self.Atom(self.data).to_dict()
        self.assertEqual(atom['title'], self.data['title'])
        self.assertEqual(atom['id'], 1)
        self.assertTrue(isinstance(atom['updated'], datetime))
        self.assertEqual(atom['category'], self.data['category'])
        self.assertEqual(atom['author'].name, self.data['author']['name'])

    def test_model_to_serial(self):
        atom = self.Atom(self.data)
        serial = atom.to_serial()
        self.assertEqual(serial['id'], 1)
        self.assertEqual(serial['updated'], atom.updated.isoformat())
        self.assertEqual(serial['category'], self.data['category'])
        self.assertEqual(serial['author'], self.data['author'])

    def test_model_late_assignment(self):
        atom = self.Atom(self.data)
        atom.id = '2'
        self.assertEqual(atom.id, 2)
        atom.updated = '2014-08-09T12:22:00Z'
        self.assertEqual(atom.updated, datetime(2014, 8, 9, 12, 22, 0, 0, utc))
        atom.category.append('physics')
        self.assertEqual(atom.category, ['blogpost', 'test', 'physics'])
        atom.author.email = 'richard@feynman.com'
        serial = atom.to_serial()
        self.assertEqual(serial['author']['name'], self.data['author']['name'])
        self.assertEqual(serial['author']['email'], 'richard@feynman.com')

    def test_model_field_assignment(self):
        atom = self.Atom(self.data)
        atom.author = {'name': 'Richard Nixon', 'email': 'dick@whitehouse.gov'}
        self.assertTrue(isinstance(atom.author, self.Person))
        self.assertEqual(atom.author.name, 'Richard Nixon')
        serial = atom.to_serial()
        self.assertEqual(serial['author']['email'], 'dick@whitehouse.gov')

    def test_update(self):
        atom = self.Atom(self.data)
        newdata = {'title': 'New Title', 'summary': 'New Summary'}
        atom.update(newdata, summary="Summary override")
        self.assertEqual(atom.title, 'New Title')
        self.assertEqual(atom.summary, 'Summary override')


class ModelFieldsProtocolTestCase(unittest.TestCase):

    def test_get_class_field(self):
        class Person1(m.Model):
            name = m.CharField()

        self.assertTrue(isinstance(Person1.get_class_field('name'),
                        m.CharField))

    def test_get_class_fields(self):
        class Person1(m.Model):
            name = m.CharField()

        fields = Person1.get_class_fields()
        self.assertEqual(fields['name'], Person1.get_class_field('name'))

    def test_add_class_field(self):
        class Person2(m.Model):
            name = m.CharField()

        Person2.add_class_field('birthday', m.DateField())
        self.assertTrue(isinstance(Person2.get_class_field('birthday'),
                        m.DateField))
        self.assertRaises(TypeError, Person2.add_class_field, 'x', 'nofield')

    def test_overwrite_field(self):
        class Person3(m.Model):
            name = m.CharField()
            birthday = m.DateTimeField()

        Person3.add_class_field('birthday', m.DateField())
        self.assertTrue(isinstance(Person3.get_class_field('birthday'),
                        m.DateField))

    def test_get_field(self):
        class Person1(m.Model):
            name = m.CharField()

        person = Person1()
        self.assertTrue(isinstance(person.get_field('name'), m.CharField))

    def test_add_field(self):
        class Person1(m.Model):
            name = m.CharField()

        person = Person1()
        person.add_field('birthday', m.DateField())
        self.assertTrue(isinstance(person.get_field('birthday'), m.DateField))
        self.assertTrue(person.__class__.get_class_field('birthday') is None)

    def test_add_field_with_bad_value(self):
        class Person1(m.Model):
            name = m.CharField()

        person = Person1()
        person.birthday = '1999-13-42'  # invalid date should raise exception

        self.assertRaises(ValueError, person.add_field, 'birthday',
                          m.DateField())

    def test_instance_field_overrides_class(self):
        class Person3(m.Model):
            name = m.CharField()
            birthday = m.DateTimeField()

        person = Person3()
        person.add_field('birthday', m.DateField())
        self.assertTrue(isinstance(person.get_field('birthday'), m.DateField))

    def test_get_all_fields(self):
        class Person3(m.Model):
            name = m.CharField()
            birthday = m.DateTimeField()

        person = Person3()
        person.add_field('birthday', m.DateField())
        fields = person.get_all_fields()
        self.assertEqual(fields['name'], Person3.get_class_field('name'))
        self.assertTrue(isinstance(fields['birthday'], m.DateField))


if __name__ == "__main__":
    unittest.main()
