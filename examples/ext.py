# -*- coding: utf-8 -*-

import os
import sys

# Add repo root to PYTHON PATH
sys.path.insert(0, os.path.abspath('..'))

import readability


def get_consumer_keys():
    """Gets Readability consumer keys from environment variables."""

    c_key = os.environ.get('READABILITY_CONSUMER_KEY')
    c_secret = os.environ.get('READABILITY_CONSUMER_SECRET')

    if all((c_key, c_secret)):
        return (c_key, c_secret)
    else:
        raise ValueError('$READABILITY_CONSUMER_SECRET must be set.')


def get_access_token():
    """Gets Readability consumer keys from environment variables."""

    o_token = os.environ.get('READABILITY_ACCESS_TOKEN')
    o_secret = os.environ.get('READABILITY_ACCESS_SECRET')

    if all((o_token, o_secret)):
        return (o_token, o_secret)
    else:
        raise ValueError('$READABILITY_ACCESS_SECRET must be set.')


def setup_rdd():
    """Boostraps Readability instance from environment."""

    try:
        c_key, c_secret = get_consumer_keys()
    except ValueError:
        print >> sys.stderr, 'READABILITY_ACCESS_TOKEN and READABILITY_ACCESS_SECRET must be set.'
        sys.exit(1)

    token = get_access_token()
    return readability.oauth(c_key, c_secret, token=token)