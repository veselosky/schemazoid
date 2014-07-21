import unittest
from datetime import date

from schemazoid import micromodels as m
from schemazoid.micromodels.models import json

# TEST Consistent interface for BaseField (to_python vs to_serial args).
# TEST BooleanField works like Django's. Strings should not be false.
# TEST Add validators to BaseField
# TEST Add required and null validation args to BaseField.
# TEST Implement NotSet value for BaseField.
# TEST Model-level validation.
# TEST Remove is_json arg from from_dict.
# TEST Remove is_json arg from set_data.
# TEST Add keymap arg to from_dict.


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
        """Model instance should have a property called _fields"""
        self.assertTrue(hasattr(self.instance, '_fields'))

    def test_field_collected(self):
        """Model property should be of correct type"""
        self.assertTrue(isinstance(self.instance._fields['name'], m.CharField))


class ClassCreationFromKwargsTestCase(unittest.TestCase):

    def setUp(self):
        class SimpleModel(m.Model):
            name = m.CharField()
            other = m.CharField()
        self.model_class = SimpleModel
        self.instance = SimpleModel(name="The name", other="The other")

    def test_class_created(self):
        """Model instance should be of type SimpleModel"""
        self.assertTrue(isinstance(self.instance, self.model_class))

    def test_fields_set(self):
        """Model instance should have a property called _fields"""
        self.assertEqual(self.instance.name, 'The name')
        self.assertEqual(self.instance.other, 'The other')


class InstanceTestCase(unittest.TestCase):

    def test_basic_data(self):
        class ThreeFieldsModel(m.Model):
            first = m.CharField()
            second = m.CharField()
            third = m.CharField()

        data = {'first': 'firstvalue', 'second': 'secondvalue'}
        instance = ThreeFieldsModel.from_dict(data)

        self.assertEqual(instance.first, data['first'])
        self.assertEqual(instance.second, data['second'])


class ModelTestCase(unittest.TestCase):

    def setUp(self):
        class Person(m.Model):
            name = m.CharField()
            age = m.IntegerField()

        self.Person = Person
        self.data = {'name': 'Eric', 'age': 18}
        self.json_data = json.dumps(self.data)

    def test_model_creation(self):
        instance = self.Person.from_dict(self.json_data, is_json=True)
        self.assertTrue(isinstance(instance, m.Model))
        self.assertEqual(instance.name, self.data['name'])
        self.assertEqual(instance.age, self.data['age'])

    def test_model_reserialization(self):
        instance = self.Person.from_dict(self.json_data, is_json=True)
        self.assertEqual(instance.to_json(), self.json_data)
        instance.name = 'John'
        self.assertEqual(json.loads(instance.to_json())['name'],
                         'John')

    def test_model_type_change_serialization(self):
        class Event(m.Model):
            time = m.DateField(format="%Y-%m-%d")

        data = {'time': '2000-10-31'}
        json_data = json.dumps(data)

        instance = Event.from_dict(json_data, is_json=True)
        output = instance.to_dict(serial=True)
        self.assertEqual(output['time'], instance.time.isoformat())
        self.assertEqual(json.loads(instance.to_json())['time'],
                         instance.time.isoformat())

    def test_model_add_field(self):
        obj = self.Person.from_dict(self.data)
        obj.add_field('gender', 'male', m.CharField())
        self.assertEqual(obj.gender, 'male')
        self.assertEqual(obj.to_dict(), dict(self.data, gender='male'))

    def test_model_late_assignment(self):
        instance = self.Person.from_dict(dict(name='Eric'))
        self.assertEqual(instance.to_dict(), dict(name='Eric'))
        instance.age = 18
        self.assertEqual(instance.to_dict(), self.data)
        instance.name = 'John'
        self.assertEqual(instance.to_dict(), dict(name='John', age=18))
        instance.age = '19'
        self.assertEqual(instance.to_dict(), dict(name='John', age=19))

        format = '%m-%d-%Y'
        today = date.today()
        today_str = today.strftime(format)

        instance.add_field('birthday', today_str,
                           m.DateField(format))
        self.assertEqual(instance.to_dict()['birthday'], today)
        instance.birthday = today
        self.assertEqual(instance.to_dict()['birthday'], today)


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
        child = self.Child.from_dict(self.data)
        self.assertEqual(child.name, self.data['name'])

    def test_child_overrides_parent_fields(self):
        child = self.Child.from_dict(self.data)
        self.assertEqual(child.age, 18.0)

    def test_grandchild_field_mro(self):
        grandchild = self.Grandchild.from_dict(self.data)
        self.assertEqual(grandchild.name, self.data['name'])
        self.assertEqual(grandchild.school, self.data['school'])
        self.assertEqual(grandchild.age, 18.0)


if __name__ == "__main__":
    unittest.main()
