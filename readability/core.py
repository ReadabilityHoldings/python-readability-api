# -*- coding: utf-8 -*-

"""
readability.core
~~~~~~~~~~~~~~~~

This module provides the core functionality of python-readability.

"""

import oauth2
import urlparse
import urllib
from cgi import parse_qsl

from .api import Readability, settings, AuthenticationError


__version__ = '0.1.1'
__license__ = 'MIT'
__author__ = 'The Readability Team'



def oauth(consumer_key, consumer_secret, callback=None, token=None):
    """Returns an authenticated Readability object, via OAuth.

    TODO: Setup callback URLs.
    TODO: Cleanup.
    """

    if token:
        r = Readability()
        r.setup_client(token, consumer_key, consumer_secret)

        return r

    else:

        consumer = oauth2.Consumer(consumer_key, consumer_secret)

        _url = settings.base_url % (settings.request_token_url,)
        r, content = oauth2.Client(consumer).request(_url, 'GET')

        if r['status'] != '200':
            raise Exception('Invalid response %s.' % (r['status']),)

        token_response = dict(parse_qsl(content))

        oauth_token = token_response['oauth_token']
        oauth_token_secret = token_response['oauth_token_secret']

        _url = settings.base_url % (settings.auth_url,)
        auth_url = '%s?oauth_token=%s' % (_url, oauth_token)
        oauth_pin = callback(auth_url)

        token = oauth2.Token(oauth_token, oauth_token_secret)
        token.set_verifier(oauth_pin)

        client = oauth2.Client(consumer, token)

        url = settings.base_url % (settings.access_token_url,)
        r, content = client.request(url, 'POST')

        ext_token = dict(parse_qsl(content))
        try:
            ext_token = (ext_token['oauth_token'], ext_token['oauth_token_secret'])
        except KeyError:
            raise AuthenticationError('Invalid Credentials.')

        return oauth(consumer_key, consumer_secret, token=ext_token)


def xauth(consumer_key, consumer_secret, username, password):
    """Returns an OAuth token pair for oauth()."""

    # Step 1: fetch oauth token from server

    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    client = oauth2.Client(consumer)
    client.add_credentials(username, password)
    client.authorizations

    params = {}
    params['x_auth_username'] = username
    params['x_auth_password'] = password
    params['x_auth_mode'] = 'client_auth'

    client.set_signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    url = settings.base_url % (settings.access_token_url,)

    r, content = client.request(
        url, method='POST', body=urllib.urlencode(params))

    token = dict(parse_qsl(content))
    try:
        token = (token['oauth_token'], token['oauth_token_secret'])
    except KeyError:
        raise AuthenticationError('Invalid Credentials.')


    return token
