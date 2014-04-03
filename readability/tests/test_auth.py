# -*- coding: utf-8 -*-

from unittest import TestCase


from readability import xauth
from readability.tests.settings import \
        CONSUMER_KEY, CONSUMER_SECRET, PASSWORD, USERNAME


class XAuthTestCase(TestCase):
    """
    Test XAuth functionality.
    """
    def test_bad_base_url(self):
        """
        If given a bad base url template, the request to the
        ACCESS_TOKEN_URL should fail and an exception be raised.
        """
        token = None
        with self.assertRaises(Exception):
            token = xauth(CONSUMER_KEY, CONSUMER_SECRET, USERNAME, PASSWORD,
                base_url_template='https://arc90.com/{0}')
        self.assertEqual(token, None)

    def test_bad_consumer_key(self):
        """
        If given a bad consumer key, the `xauth` method should raise
        an exception.
        """
        token = None
        with self.assertRaises(Exception):
            token = \
                xauth('bad consumer key', CONSUMER_SECRET, USERNAME, PASSWORD)
        self.assertEqual(token, None)

    def test_bad_consumer_secret(self):
        """
        If given a bad consumer key, the `xauth` method should raise
        an exception.
        """
        token = None
        with self.assertRaises(Exception):
            token = \
                xauth(CONSUMER_KEY, 'bad consumer secret', USERNAME, PASSWORD)
        self.assertEqual(token, None)

    def test_bad_username(self):
        """
        If given a bad username, an exception should be raised.
        """
        token = None
        with self.assertRaises(Exception):
            token = \
                xauth(CONSUMER_KEY, CONSUMER_SECRET, 'bad username', PASSWORD)
        self.assertEqual(token, None)

    def test_bad_password(self):
        """
        If given a bad password, an exception should be raised.
        """
        token = None
        with self.assertRaises(Exception):
            token = \
                xauth(CONSUMER_KEY, CONSUMER_SECRET, USERNAME, 'badpassword')
        self.assertEqual(token, None)

    def test_successful_auth(self):
        """
        Test getting a token with proper creds
        """
        token = xauth(CONSUMER_KEY, CONSUMER_SECRET, USERNAME, PASSWORD)
        self.assertEqual(len(token), 2)
