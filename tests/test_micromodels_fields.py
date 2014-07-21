import unittest
from datetime import date, time, datetime

from schemazoid import micromodels as m


class CharFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = m.CharField()

    def test_string_conversion(self):
        self.field.populate('somestring')
        self.assertEqual(self.field.to_python(), 'somestring')

    def test_none_conversion(self):
        """CharField should convert None to empty string"""
        self.field.populate(None)
        self.assertEqual(self.field.to_python(), '')


class IntegerFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = m.IntegerField()

    def test_integer_conversion(self):
        self.field.populate(123)
        self.assertEqual(self.field.to_python(), 123)

    def test_float_conversion(self):
        self.field.populate(123.4)
        self.assertEqual(self.field.to_python(), 123)

    def test_string_conversion(self):
        self.field.populate('123')
        self.assertEqual(self.field.to_python(), 123)

    def test_none_conversion(self):
        """IntegerField should convert None to 0"""
        self.field.populate(None)
        self.assertEqual(self.field.to_python(), 0)


class FloatFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = m.FloatField()

    def test_float_conversion(self):
        self.field.populate(123.4)
        self.assertEqual(self.field.to_python(), 123.4)

    def test_integer_conversion(self):
        self.field.populate(123)
        self.assertEqual(self.field.to_python(), 123.0)

    def test_string_conversion(self):
        self.field.populate('123.4')
        self.assertEqual(self.field.to_python(), 123.4)

    def test_none_conversion(self):
        """FloatField should convert None to 0.0"""
        self.field.populate(None)
        self.assertEqual(self.field.to_python(), 0.0)


class BooleanFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = m.BooleanField()

    def test_true_conversion(self):
        self.field.populate(True)
        self.assertEqual(self.field.to_python(), True)

    def test_false_conversion(self):
        self.field.populate(False)
        self.assertEqual(self.field.to_python(), False)

    def test_string_conversion(self):
        """BooleanField uses Python's boolean rules for non-boolean values,
        with one exception: a string containing "false" (case insensitive)
        or "0" will evaluate False."""
        self.field.populate('true')
        self.assertEqual(self.field.to_python(), True)
        self.field.populate('True')
        self.assertEqual(self.field.to_python(), True)
        self.field.populate('False')
        self.assertEqual(self.field.to_python(), False)
        self.field.populate('false strings are not false')
        self.assertEqual(self.field.to_python(), True)
        self.field.populate('0')
        self.assertEqual(self.field.to_python(), False)

    def test_integer_conversion(self):
        """BooleanField should convert 0 to False, all other integers
        to True"""
        self.field.populate(0)
        self.assertEqual(self.field.to_python(), False)
        self.field.populate(-100)
        self.assertEqual(self.field.to_python(), True)
        self.field.populate(100)
        self.assertEqual(self.field.to_python(), True)


class DateTimeFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.format = "%a %b %d %H:%M:%S +0000 %Y"
        self.datetimestring = "Tue Mar 21 20:50:14 +0000 2006"
        self.field = m.DateTimeField(format=self.format)

    def test_format_conversion(self):
        self.field.populate(self.datetimestring)
        converted = self.field.to_python()
        self.assertTrue(isinstance(converted, datetime))
        self.assertEqual(converted.strftime(self.format), self.datetimestring)

    def test_iso8601_conversion(self):
        import pytz  # sigh dateutil.tz lib not portable py2-py3 as of 2.2

        field = m.DateTimeField()
        field.populate("2010-07-13T14:01:00Z")
        result = field.to_python()
        expected = datetime(2010, 7, 13, 14, 1, 0, tzinfo=pytz.utc)
        self.assertEqual(expected, result)

        field = m.DateTimeField()
        field.populate("2010-07-13T14:02:00-05:00")
        result = field.to_python()
        cdt = pytz.timezone("America/Chicago")  # DST, so -5 is central time
        expected = cdt.localize(datetime(2010, 7, 13, 14, 2, 0))

        self.assertEqual(expected, result)

        field = m.DateTimeField()
        field.populate("20100713T140200-05:00")
        result = field.to_python()
        expected = cdt.localize(datetime(2010, 7, 13, 14, 2, 0))

        self.assertEqual(expected, result)

    def test_iso8601_to_serial(self):

        field = m.DateTimeField()
        field.populate("2010-07-13T14:01:00Z")
        native = field.to_python()
        expected = "2010-07-13T14:01:00+00:00"
        result = field.to_serial(native)

        self.assertEqual(expected, result)

        field = m.DateTimeField()
        field.populate("2010-07-13T14:02:00-05:00")
        native = field.to_python()
        expected = "2010-07-13T14:02:00-05:00"
        result = field.to_serial(native)

        self.assertEqual(expected, result)


class DateFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.format = "%Y-%m-%d"
        self.datestring = "2010-12-28"
        self.field = m.DateField(format=self.format)

    def test_format_conversion(self):
        self.field.populate(self.datestring)
        converted = self.field.to_python()
        self.assertTrue(isinstance(converted, date))
        self.assertEqual(converted.strftime(self.format), self.datestring)

    def test_iso8601_conversion(self):
        field = m.DateField()
        field.populate("2010-12-28")
        result = field.to_python()
        expected = date(2010, 12, 28)
        self.assertEqual(expected, result)

        field = m.DateField()
        field.populate("20101228")
        result = field.to_python()
        expected = date(2010, 12, 28)
        self.assertEqual(expected, result)


class TimeFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.format = "%H:%M:%S"
        self.timestring = "09:33:30"
        self.field = m.TimeField(format=self.format)

    def test_format_conversion(self):
        self.field.populate(self.timestring)
        converted = self.field.to_python()
        self.assertTrue(isinstance(converted, time))
        self.assertEqual(converted.strftime(self.format), self.timestring)

    def test_iso8601_conversion(self):
        field = m.TimeField()
        field.populate("09:33:30")
        result = field.to_python()
        expected = time(9, 33, 30)
        self.assertEqual(expected, result)

    def test_iso8601_without_delimiters(self):
        field = m.TimeField()
        field.populate("093331")
        result = field.to_python()
        expected = time(9, 33, 31)
        self.assertEqual(expected, result)

    def test_handles_datetime(self):
        field = m.TimeField()
        field.populate(datetime(2010, 7, 21, 16, 44, 0))
        result = field.to_python()
        expected = time(16, 44, 0)
        self.assertEqual(expected, result)


class ModelFieldTestCase(unittest.TestCase):

    def test_model_field_creation(self):
        class IsASubModel(m.Model):
            first = m.CharField()

        class HasAModelField(m.Model):
            first = m.ModelField(IsASubModel)

        data = {'first': {'first': 'somevalue'}}
        instance = HasAModelField.from_dict(data)
        self.assertTrue(isinstance(instance.first, IsASubModel))
        self.assertEqual(instance.first.first, data['first']['first'])

    def test_model_field_to_serial(self):
        class User(m.Model):
            name = m.CharField()

        class Post(m.Model):
            title = m.CharField()
            author = m.ModelField(User)

        data = {'title': 'Test Post', 'author': {'name': 'Eric Martin'}}
        post = Post.from_dict(data)
        self.assertEqual(post.to_dict(serial=True), data)

    def test_related_name(self):
        class User(m.Model):
            name = m.CharField()

        class Post(m.Model):
            title = m.CharField()
            author = m.ModelField(User, related_name="post")

        data = {'title': 'Test Post', 'author': {'name': 'Eric Martin'}}
        post = Post.from_dict(data)
        self.assertEqual(post.author.post, post)
        self.assertEqual(post.to_dict(serial=True), data)

    def test_failing_modelfield(self):
        class SomethingExceptional(Exception):
            pass

        class User(m.Model):
            name = m.CharField()

            @classmethod
            def from_dict(cls, *args, **kwargs):
                raise SomethingExceptional("opps.")

        class Post(m.Model):
            title = m.CharField()
            author = m.ModelField(User)

        data = {'title': 'Test Post', 'author': {'name': 'Eric Martin'}}
        self.assertRaises(SomethingExceptional, Post.from_dict,
                          data)


class ModelCollectionFieldTestCase(unittest.TestCase):

    def test_model_collection_field_creation(self):
        class IsASubModel(m.Model):
            first = m.CharField()

        class HasAModelCollectionField(m.Model):
            first = m.ModelCollectionField(IsASubModel)

        data = {'first': [{'first': 'somevalue'}, {'first': 'anothervalue'}]}
        instance = HasAModelCollectionField.from_dict(data)
        self.assertTrue(isinstance(instance.first, list))
        for item in instance.first:
            self.assertTrue(isinstance(item, IsASubModel))
        self.assertEqual(instance.first[0].first, data['first'][0]['first'])
        self.assertEqual(instance.first[1].first, data['first'][1]['first'])

    def test_model_collection_field_with_no_elements(self):
        class IsASubModel(m.Model):
            first = m.CharField()

        class HasAModelCollectionField(m.Model):
            first = m.ModelCollectionField(IsASubModel)

        data = {'first': []}
        instance = HasAModelCollectionField.from_dict(data)
        self.assertEqual(instance.first, [])

    def test_model_collection_to_serial(self):
        class Post(m.Model):
            title = m.CharField()

        class User(m.Model):
            name = m.CharField()
            posts = m.ModelCollectionField(Post)

        data = {
            'name': 'Eric Martin',
            'posts': [
                {'title': 'Post #1'},
                {'title': 'Post #2'}
            ]
        }

        eric = User.from_dict(data)
        processed = eric.to_dict(serial=True)
        self.assertEqual(processed, data)

    def test_related_name(self):
        class Post(m.Model):
            title = m.CharField()

        class User(m.Model):
            name = m.CharField()
            posts = m.ModelCollectionField(Post, related_name="author")

        data = {
            'name': 'Eric Martin',
            'posts': [
                {'title': 'Post #1'},
                {'title': 'Post #2'}
            ]
        }

        eric = User.from_dict(data)
        processed = eric.to_dict(serial=True)
        for post in eric.posts:
            self.assertEqual(post.author, eric)

        self.assertEqual(processed, data)


class FieldCollectionFieldTestCase(unittest.TestCase):

    def test_field_collection_field_creation(self):
        class HasAFieldCollectionField(m.Model):
            first = m.FieldCollectionField(m.CharField())

        data = {'first': ['one', 'two', 'three']}
        instance = HasAFieldCollectionField.from_dict(data)
        self.assertTrue(isinstance(instance.first, list))
        self.assertTrue(len(data['first']), len(instance.first))
        for index, value in enumerate(data['first']):
            self.assertEqual(instance.first[index], value)

    def test_field_collection_field_to_serial(self):
        class Person(m.Model):
            aliases = m.FieldCollectionField(m.CharField())
            events = m.FieldCollectionField(
                m.DateField('%Y-%m-%d', serial_format='%m-%d-%Y'))

        data = {
            'aliases': ['Joe', 'John', 'Bob'],
            'events': ['2011-01-30', '2011-04-01']
        }

        p = Person.from_dict(data)
        serial = p.to_dict(serial=True)
        self.assertEqual(serial['aliases'], data['aliases'])
        self.assertEqual(serial['events'][0], '01-30-2011')
