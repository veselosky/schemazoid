import pytz  # sigh dateutil.tz lib not portable py2-py3 as of 2.2
import unittest

from datetime import date, time, datetime

from schemazoid import micromodels as m


class BaseFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = m.BaseField()

    def test_to_python(self):
        self.assertEqual(self.field.to_python('somestring'), 'somestring')

    def test_to_serial(self):
        self.assertEqual(self.field.to_serial('somestring'), 'somestring')


class CharFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = m.CharField()

    def test_string_conversion(self):
        self.assertEqual(self.field.to_python('somestring'), 'somestring')

    def test_none_conversion(self):
        """CharField should convert None to empty string"""
        self.assertEqual(self.field.to_python(None), '')

    def test_integer_conversion(self):
        self.assertEqual(self.field.to_python(3), '3')

    def test_float_conversion(self):
        self.assertEqual(self.field.to_python(3.3), '3.3')

    def test_boolean_conversion(self):
        self.assertEqual(self.field.to_python(True), 'True')
        self.assertEqual(self.field.to_python(False), 'False')

    def test_datetime_conversion(self):
        now = datetime.now()
        self.assertEqual(self.field.to_python(now), now.isoformat())

    def test_date_conversion(self):
        today = datetime.now().date()
        self.assertEqual(self.field.to_python(today), today.isoformat())


class IntegerFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = m.IntegerField()

    def test_integer_conversion(self):
        self.assertEqual(self.field.to_python(123), 123)

    def test_float_conversion(self):
        self.assertEqual(self.field.to_python(123.4), 123)

    def test_string_conversion(self):
        self.assertEqual(self.field.to_python('123'), 123)

    def test_none_conversion(self):
        """IntegerField should convert None to 0"""
        self.assertEqual(self.field.to_python(None), 0)


class FloatFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = m.FloatField()

    def test_float_conversion(self):
        self.assertEqual(self.field.to_python(123.4), 123.4)

    def test_integer_conversion(self):
        self.assertEqual(self.field.to_python(123), 123.0)

    def test_string_conversion(self):
        self.assertEqual(self.field.to_python('123.4'), 123.4)

    def test_none_conversion(self):
        """FloatField should convert None to 0.0"""
        self.assertEqual(self.field.to_python(None), 0.0)


class BooleanFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.field = m.BooleanField()

    def test_none_conversion(self):
        self.assertEqual(self.field.to_python(None), False)

    def test_true_conversion(self):
        self.assertEqual(self.field.to_python(True), True)

    def test_false_conversion(self):
        self.assertEqual(self.field.to_python(False), False)

    def test_string_conversion(self):
        """BooleanField uses Python's boolean rules for non-boolean values,
        with one exception: a string containing "false" (case insensitive)
        or "0" will evaluate False."""
        self.assertEqual(self.field.to_python('true'), True)
        self.assertEqual(self.field.to_python('True'), True)
        self.assertEqual(self.field.to_python('False'), False)
        self.assertEqual(self.field.to_python('false strings not false'), True)
        self.assertEqual(self.field.to_python('0'), False)

    def test_integer_conversion(self):
        """BooleanField should convert 0 to False, all other integers
        to True"""
        self.assertEqual(self.field.to_python(0), False)
        self.assertEqual(self.field.to_python(-100), True)
        self.assertEqual(self.field.to_python(100), True)


class DateTimeFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.format = "%a %b %d %H:%M:%S +0000 %Y"
        self.datetimestring = "Tue Mar 21 20:50:14 +0000 2006"
        self.format_field = m.DateTimeField(format=self.format)
        self.field = m.DateTimeField()

    def test_format_conversion(self):
        converted = self.format_field.to_python(self.datetimestring)
        self.assertTrue(isinstance(converted, datetime))
        self.assertEqual(converted.strftime(self.format), self.datetimestring)

    def test_datetime(self):
        expected = datetime(2010, 7, 13, 14, 1, 0, tzinfo=pytz.utc)
        self.assertEqual(self.field.to_python(expected), expected)

    def test_none_conversion(self):
        self.assertEqual(self.field.to_python(None), None)

    def test_iso8601_utc(self):
        result = self.field.to_python("2010-07-13T14:01:00Z")
        expected = datetime(2010, 7, 13, 14, 1, 0, tzinfo=pytz.utc)
        self.assertEqual(expected, result)

    def test_iso8601_with_timezone(self):
        result = self.field.to_python("2010-07-13T14:02:00-05:00")
        cdt = pytz.timezone("America/Chicago")  # DST, so -5 is central time
        expected = cdt.localize(datetime(2010, 7, 13, 14, 2, 0))

        self.assertEqual(expected, result)

    def test_iso8601_compact(self):
        result = self.field.to_python("20100713T140200-05:00")
        cdt = pytz.timezone("America/Chicago")  # DST, so -5 is central time
        expected = cdt.localize(datetime(2010, 7, 13, 14, 2, 0))

        self.assertEqual(expected, result)

    def test_iso8601_to_serial_utc(self):
        native = self.field.to_python("2010-07-13T14:01:00Z")
        expected = "2010-07-13T14:01:00+00:00"
        result = self.field.to_serial(native)

        self.assertEqual(expected, result)

    def test_iso8601_to_serial_with_timezone(self):
        native = self.field.to_python("2010-07-13T14:02:00-05:00")
        expected = "2010-07-13T14:02:00-05:00"
        result = self.field.to_serial(native)

        self.assertEqual(expected, result)


class DateFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.format = "%Y-%m-%d"
        self.datestring = "2010-12-28"
        self.field = m.DateField(format=self.format)

    def test_none_conversion(self):
        self.assertEqual(self.field.to_python(None), None)

    def test_date(self):
        expected = date(2014, 8, 1)
        self.assertEqual(self.field.to_python(expected), expected)

    def test_format_conversion(self):
        converted = self.field.to_python(self.datestring)
        self.assertTrue(isinstance(converted, date))
        self.assertEqual(converted.strftime(self.format), self.datestring)

    def test_iso8601_conversion(self):
        field = m.DateField()
        result = field.to_python("2010-12-28")
        expected = date(2010, 12, 28)
        self.assertEqual(expected, result)

    def test_iso8601_compact(self):
        field = m.DateField()
        result = field.to_python("20101228")
        expected = date(2010, 12, 28)
        self.assertEqual(expected, result)


class TimeFieldTestCase(unittest.TestCase):

    def setUp(self):
        self.format = "%H.%M.%S"
        self.timestring = "09.33.30"
        self.format_field = m.TimeField(format=self.format)
        self.field = m.TimeField()

    def test_none_conversion(self):
        self.assertEqual(self.field.to_python(None), None)

    def test_time(self):
        expected = datetime.now().time()
        self.assertEqual(self.field.to_python(expected), expected)

    def test_format_conversion(self):
        converted = self.format_field.to_python(self.timestring)
        self.assertTrue(isinstance(converted, time))
        self.assertEqual(converted.strftime(self.format), self.timestring)

    def test_iso8601_conversion(self):
        result = self.field.to_python("09:33:30")
        expected = time(9, 33, 30)
        self.assertEqual(expected, result)

    def test_iso8601_without_delimiters(self):
        result = self.field.to_python("093331")
        expected = time(9, 33, 31)
        self.assertEqual(expected, result)

    def test_handles_datetime(self):
        result = self.field.to_python(datetime(2010, 7, 21, 16, 44, 0))
        expected = time(16, 44, 0)
        self.assertEqual(expected, result)
