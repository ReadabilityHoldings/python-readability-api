# -*- coding: utf-8 -*-

import os
import sys

# Add repo root to PYTHON PATH
sys.path.insert(0, os.path.abspath('..'))

import readability

readability.settings.base_url = 'http://127.0.0.1:8000/api/rest/v1/%s'


def get_consumer_keys():
    """Gets Readability consumer keys from environment variables."""

    c_key = os.environ.get('READABILITY_CONSUMER_KEY')
    c_secret = os.environ.get('READABILITY_CONSUMER_SECRET')

    if all((c_key, c_secret)):
        return (c_key, c_secret)
    else:
        raise ValueError('$READABILITY_CONSUMER_SECRET must be set.')


def get_oauth_token():
    """Gets Readability consumer keys from environment variables."""

    o_token = os.environ.get('READABILITY_OAUTH_TOKEN')
    o_secret = os.environ.get('READABILITY_OAUTH_SECRET')

    if all((o_token, o_secret)):
        return (o_token, o_secret)
    else:
        raise ValueError('$READABILITY_OAUTH_SECRET must be set.')
