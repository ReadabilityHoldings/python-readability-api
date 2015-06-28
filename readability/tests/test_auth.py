# -*- coding: utf-8 -*-

# Bad hack. I only installed unittest2 locally in my virtualenv
# for Python 2.6.7
try:
    import unittest2 as unittest
except ImportError:
    import unittest


from readability import xauth


class XAuthTestCase(unittest.TestCase):
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
            token = xauth(base_url_template='https://arc90.com/{0}')
        self.assertEqual(token, None)

    def test_bad_consumer_key(self):
        """
        If given a bad consumer key, the `xauth` method should raise
        an exception.
        """
        token = None
        with self.assertRaises(Exception):
            token = xauth(consumer_key='bad consumer key')
        self.assertEqual(token, None)

    def test_bad_consumer_secret(self):
        """
        If given a bad consumer key, the `xauth` method should raise
        an exception.
        """
        token = None
        with self.assertRaises(Exception):
            token = xauth(consumer_secret='bad consumer secret')
        self.assertEqual(token, None)

    def test_bad_username(self):
        """
        If given a bad username, an exception should be raised.
        """
        token = None
        with self.assertRaises(Exception):
            token = xauth(username='bad username')
        self.assertEqual(token, None)

    def test_bad_password(self):
        """
        If given a bad password, an exception should be raised.
        """
        token = None
        with self.assertRaises(Exception):
            token = xauth(password='badpassword')
        self.assertEqual(token, None)

    def test_successful_auth(self):
        """
        Test getting a token with proper creds
        """
        # Credentials should be set as environment variables when running tests
        token = xauth()
        self.assertEqual(len(token), 2)


if __name__ == '__main__':
    unittest.main()
