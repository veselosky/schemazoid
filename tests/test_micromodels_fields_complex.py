import pytest
import unittest
from schemazoid import micromodels as m


class ModelFieldTestCase(unittest.TestCase):

    def test_model_field_creation(self):
        class IsASubModel(m.Model):
            first = m.CharField()

        class HasAModelField(m.Model):
            first = m.ModelField(IsASubModel)

        data = {'first': {'first': 'somevalue'}}
        instance = HasAModelField(data)
        self.assertTrue(isinstance(instance.first, IsASubModel))
        self.assertEqual(instance.first.first, data['first']['first'])

    def test_model_field_to_serial(self):
        class User(m.Model):
            name = m.CharField()

        class Post(m.Model):
            title = m.CharField()
            author = m.ModelField(User)

        data = {'title': 'Test Post', 'author': {'name': 'Eric Martin'}}
        post = Post(data)
        self.assertEqual(post.to_dict(serial=True), data)

    def test_related_name(self):
        class User(m.Model):
            name = m.CharField()

        class Post(m.Model):
            title = m.CharField()
            author = m.ModelField(User, related_name="post")

        data = {'title': 'Test Post', 'author': {'name': 'Eric Martin'}}
        post = Post(data)
        self.assertEqual(post.author.post, post)
        self.assertEqual(post.to_dict(serial=True), data)

    @pytest.mark.skipif(True, reason="TODO")
    def test_failing_modelfield(self):
        """TODO Test when model in the field fails validation"""
        pass


class ModelCollectionFieldTestCase(unittest.TestCase):

    def test_model_collection_field_creation(self):
        class IsASubModel(m.Model):
            first = m.CharField()

        class HasAModelCollectionField(m.Model):
            first = m.ModelCollectionField(IsASubModel)

        data = {'first': [{'first': 'somevalue'}, {'first': 'anothervalue'}]}
        instance = HasAModelCollectionField(data)
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
        instance = HasAModelCollectionField(data)
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

        eric = User(data)
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

        eric = User(data)
        processed = eric.to_dict(serial=True)
        for post in eric.posts:
            self.assertEqual(post.author, eric)

        self.assertEqual(processed, data)


class FieldCollectionFieldTestCase(unittest.TestCase):

    def test_field_collection_field_creation(self):
        class HasAFieldCollectionField(m.Model):
            first = m.FieldCollectionField(m.CharField())

        data = {'first': ['one', 'two', 'three']}
        instance = HasAFieldCollectionField(data)
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

        p = Person(data)
        serial = p.to_dict(serial=True)
        self.assertEqual(serial['aliases'], data['aliases'])
        self.assertEqual(serial['events'][0], '01-30-2011')
