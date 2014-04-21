# -*- coding: utf-8 -*-

"""
readability.auth
~~~~~~~~~~~~~~~~

This module provides the xauth functionality for the Readability
Reader API.

"""

import logging
from urllib import parse

import requests

from cgi import parse_qsl

from oauthlib.oauth1 import Client
from requests_oauthlib import OAuth1

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
    client = Client(consumer_key, client_secret=consumer_secret)
    url = base_url_template.format(ACCESS_TOKEN_URL)
    additional_auth_headers = {
        'x_auth_username': username,
        'x_auth_password': password,
        'x_auth_mode': 'client_auth'
    }

    uri, headers, body = client.sign(url, headers=additional_auth_headers)
    response = requests.post(uri, headers=headers)
    import pdb; pdb.set_trace()
    logger.debug('POST to %s.', uri)

    token = dict(parse_qsl(response.content))
    try:
        token = (token['oauth_token'], token['oauth_token_secret'])
    except KeyError:
        raise Exception('Invalid Credentials.')

    return token
