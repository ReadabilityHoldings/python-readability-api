# -*- coding: utf-8 -*-

"""
readability.auth
~~~~~~~~~~~~~~~~

This module provides the xauth functionality for the Readability
Reader API.

"""
from __future__ import unicode_literals

import logging
import sys

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

# TODO FIX THIS
#from .clients import DEFAULT_READER_URL_TEMPLATE


logger = logging.getLogger(__name__)
ACCESS_TOKEN_URL = 'oauth/access_token/'

DEFAULT_READER_URL_TEMPLATE = 'https://www.readability.com/api/rest/v1/{0}'


def xauth(consumer_key, consumer_secret, username, password,
    base_url_template=DEFAULT_READER_URL_TEMPLATE):
    """
    Returns an OAuth token that can be used with clients.ReaderClient.

    :param consumer_key:  Readability consumer key
    :param consumer_secret: Readability consumer secret
    :param username: A username
    :param password: A password
    :param base_url_template: Template for generating Readability API urls.
    """
    client = Client(consumer_key, client_secret=consumer_secret, signature_type='BODY')
    url = base_url_template.format(ACCESS_TOKEN_URL)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    params = {
        'x_auth_username': username,
        'x_auth_password': password,
        'x_auth_mode': 'client_auth'
    }

    uri, headers, body = client.sign(url, http_method='POST', body=urlencode(params), headers=headers)
    response = requests.post(uri, data=body)
    logger.debug('POST to %s.', uri)

    token = parse_qs(response.content)
    try:
        # The indexes below are a little weird. parse_qs above gives us
        # back a dict where each value is a list. We want the first value
        # in those lists.
        token = (token[b'oauth_token'][0], token[b'oauth_token_secret'][0])
    except KeyError:
        raise Exception('Invalid Credentials.')

    return token
