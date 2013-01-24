# -*- coding: utf-8 -*-

from datetime import datetime
from unittest import TestCase

from readability.utils import \
    cast_datetime_filter, cast_integer_filter, filter_args_to_dict


class CastDatetimeFilterTestCase(TestCase):
    """Tests for the `cast_datetime_filter` function.

    """
    def test_int(self):
        """Pass an int. Should raise a `ValueError`

        """
        with self.assertRaises(ValueError):
            cast_datetime_filter(1)

    def test_non_iso_string(self):
        """Pass a string that's not in ISO format.

        Should get a string back that's in ISO format.

        """
        date_string = '08-03-2010'
        expected_iso = cast_datetime_filter(date_string)
        self.assertEqual(expected_iso, '2010-08-03T00:00:00')

    def test_datetime_object(self):
        """Pass a datetime object. Should get a string back in ISO format.

        """
        now = datetime.now()
        expected_output = now.isoformat()
        actual_output = cast_datetime_filter(now)
        self.assertEqual(actual_output, expected_output)


class CastIntegerFilter(TestCase):
    """Test for the `cast_integer_filter` function.

    """
    def test_int(self):
        """Pass an int. Should get it back.

        """
        value_to_cast = 1
        output = cast_integer_filter(value_to_cast)
        self.assertEqual(value_to_cast, output)

    def test_false(self):
        """Pass a boolean False. Should get a 0 back.

        """
        output = cast_integer_filter(False)
        expected_output = 0
        self.assertEqual(output, expected_output)

    def test_true(self):
        """Pass a boolean True. Should get a 1 back.

        """
        output = cast_integer_filter(True)
        expected_output = 1
        self.assertEqual(output, expected_output)

    def test_numeric_string(self):
        """Pass a numeric string. Should get the integer version back.

        """
        numeric_string = '123'
        expected_output = 123
        output = cast_integer_filter(numeric_string)
        self.assertEqual(expected_output, output)


class FilterArgsToDictTestCase(TestCase):
    """Test for the `filter_args_to_dict` function.

    """

    def test_all_bad_filter_keys(self):
        """Pass a dict who's keys are not in the acceptable filter list.

        Should get an empty dict back.
        """
        filters = {
            'date_deleted': '08-08-2010',
            'date_updated': '08-08-2011',
            'liked': 1
        }

        acceptable_filters = ['favorite', 'archive']
        expected_empty = filter_args_to_dict(filters, acceptable_filters)
        self.assertEqual(expected_empty, {})

    def test_some_bad_filter_keys(self):
        """Pass a mixture of good and bad filter keys.

        """
        filters = {
            'favorite': True,
            'archive': False
        }
        bad_filters = {
            'date_deleted': '08-08-2010',
            'date_updated': '08-08-2011',
            'liked': 1
        }
        acceptable_filter_keys = filters.keys()

        # add bad filters to filters dict
        filters.update(bad_filters)
        filter_dict = filter_args_to_dict(filters, acceptable_filter_keys)
        self.assertEqual(set(filter_dict.keys()), set(acceptable_filter_keys))

    def test_casting_of_integer_filters(self):
        """Pass keys that correspond to integer filters.

        """
        filters = {
            'favorite': True,
            'archive': False
        }
        acceptable_filter_keys = filters.keys()
        filter_dict = filter_args_to_dict(filters, acceptable_filter_keys)
        self.assertEqual(set(filter_dict.keys()), set(acceptable_filter_keys))
        self.assertEqual(filter_dict['favorite'], 1)
        self.assertEqual(filter_dict['archive'], 0)

    def test_casting_of_datetime_filters(self):
        """Pass keys that correspond to datetime filters.

        """
        now = datetime.now()
        filters = {
            'archived_since': '08-08-2010',
            'favorited_since': now
        }
        acceptable_filter_keys = filters.keys()
        filter_dict = filter_args_to_dict(filters, acceptable_filter_keys)
        self.assertEqual(set(filter_dict.keys()), set(acceptable_filter_keys))
        self.assertEqual(filter_dict['archived_since'], '2010-08-08T00:00:00')
        self.assertEqual(filter_dict['favorited_since'], now.isoformat())
