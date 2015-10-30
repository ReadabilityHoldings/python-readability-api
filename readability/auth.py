# -*- coding: utf-8 -*-

"""
readability.auth
~~~~~~~~~~~~~~~~

This module provides the xauth functionality for the Readability
Reader API.

"""
from __future__ import unicode_literals

import logging

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode
try:
    from urllib.parse import parse_qs
except ImportError:
    from urlparse import parse_qs


import requests

from oauthlib.oauth1 import Client

from readability.clients import DEFAULT_READER_URL_TEMPLATE
from readability.core import required_from_env

logger = logging.getLogger(__name__)
ACCESS_TOKEN_URL = 'oauth/access_token/'



def xauth(base_url_template=DEFAULT_READER_URL_TEMPLATE, **xargs):
    """
    Returns an OAuth token tuple that can be used with clients.ReaderClient.

    :param base_url_template: Template for generating Readability API urls.
    :param consumer_key:  Readability consumer key, otherwise read from READABILITY_CONSUMER_KEY.
    :param consumer_secret: Readability consumer secret, otherwise read from READABILITY_CONSUMER_SECRET.
    :param username: A username, otherwise read from READABILITY_USERNAME.
    :param password: A password, otherwise read from READABILITY_PASSWORD.

    """
    consumer_key = xargs.get('consumer_key') or required_from_env('READABILITY_CONSUMER_KEY')
    consumer_secret = xargs.get('consumer_secret') or required_from_env('READABILITY_CONSUMER_SECRET')
    username = xargs.get('username') or required_from_env('READABILITY_USERNAME')
    password = xargs.get('password') or required_from_env('READABILITY_PASSWORD')

    client = Client(consumer_key, client_secret=consumer_secret, signature_type='BODY')
    url = base_url_template.format(ACCESS_TOKEN_URL)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {
        'x_auth_username': username,
        'x_auth_password': password,
        'x_auth_mode': 'client_auth'
    }

    uri, headers, body = client.sign(url,
        http_method='POST',
        body=urlencode(params),
        headers=headers)

    response = requests.post(uri, data=body)
    logger.debug('POST to %s.', uri)

    token = parse_qs(response.content)
    try:
        # The indexes below are a little weird. parse_qs above gives us
        # back a dict where each value is a list. We want the first value
        # in those lists.
        token = (token[b'oauth_token'][0].decode(), token[b'oauth_token_secret'][0].decode())
    except KeyError:
        raise ValueError('Invalid Credentials.')

    return token
