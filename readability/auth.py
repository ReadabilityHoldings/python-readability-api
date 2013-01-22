# -*- coding: utf-8 -*-

"""
readability.core
~~~~~~~~~~~~~~~~

This module provides the authentication functionality for the Readability
HTTP API.

"""

import oauth2
import urllib
from cgi import parse_qsl


__version__ = '0.2.0'
__license__ = 'MIT'
__author__ = 'The Readability Team'

DEFAULT_BASE_URL_TEMPLATE = 'https://readability.com/api/rest/v1/{0}'
REQUEST_TOKEN_URL = 'oauth/request_token/'
ACCESS_TOKEN_URL = 'oauth/access_token/'
AUTH_URL = 'oauth/authorize/'


def oauth(consumer_key, consumer_secret, callback=None,
    base_url_template=DEFAULT_BASE_URL_TEMPLATE):
    """Returns an OAuth token that can be used with clients.BaseClient.

    :param consumer_key: Your Readability consumer key
    :type consumer_key: string

    :param consumer_secret: Your Readability consumer secret
    :type consumer_key: string

    :param base_url_template: Template for generating Readability API urls.
    :type base_url_template: string

    """
    consumer = oauth2.Consumer(consumer_key, consumer_secret)

    _url = base_url_template.format(REQUEST_TOKEN_URL)
    r, content = oauth2.Client(consumer).request(_url, 'GET')

    if r.status != '200':
        raise Exception('Invalid response {0}.'.format(r['status']))

    token_response = dict(parse_qsl(content))

    oauth_token = token_response['oauth_token']
    oauth_token_secret = token_response['oauth_token_secret']

    _url = base_url_template.format(AUTH_URL)
    auth_url = '{0}?oauth_token={1}'.format(_url, oauth_token)
    oauth_pin = callback(auth_url)

    token = oauth2.Token(oauth_token, oauth_token_secret)
    token.set_verifier(oauth_pin)

    client = oauth2.Client(consumer, token)

    url = base_url_template.format(ACCESS_TOKEN_URL)
    r, content = client.request(url, 'POST')

    ext_token = dict(parse_qsl(content))
    try:
        ext_token = (ext_token['oauth_token'], ext_token['oauth_token_secret'])
    except KeyError:
        raise Exception('Invalid Credentials.')

    return ext_token


def xauth(consumer_key, consumer_secret, username, password,
    base_url_template=DEFAULT_BASE_URL_TEMPLATE):
    """Returns an OAuth token pair for oauth().

    :param consumer_key: Your Readability consumer key
    :type consumer_key: string

    :param consumer_secret: Your Readability consumer secret
    :type consumer_key: string

    :param username: A username
    :type username: string

    :param password: A password
    :type username: string

    :param base_url_template: Template for generating Readability API urls.
    :type base_url_template: string

    """
    # fetch oauth token from server
    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    client = oauth2.Client(consumer)
    client.add_credentials(username, password)
    client.authorizations

    params = {}
    params['x_auth_username'] = username
    params['x_auth_password'] = password
    params['x_auth_mode'] = 'client_auth'

    client.set_signature_method = oauth2.SignatureMethod_HMAC_SHA1()
    url = base_url_template.format(ACCESS_TOKEN_URL)

    r, content = client.request(
        url, method='POST', body=urllib.urlencode(params))

    token = dict(parse_qsl(content))
    try:
        token = (token['oauth_token'], token['oauth_token_secret'])
    except KeyError:
        raise Exception('Invalid Credentials.')

    return token
