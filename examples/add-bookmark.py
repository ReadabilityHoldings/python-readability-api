#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
add-bookmark.py
~~~~~~~~~~~~~~~~~

This module is an example of how to harness the Readability API w/ oAuth.

This module expects the following environment variables to be set:

- READABILITY_CONSUMER_KEY
- READABILITY_CONSUMER_SECRET
- READABILITY_ACCESS_TOKEN
- READABILITY_ACCESS_SECRET

Once you have your consumer keys set up, run the following to get your OAuth
tokens:

    $ ./login-xauth.py <username> <password>

"""

import sys

from ext import readability
from ext import get_consumer_keys, get_access_token

readability.settings.base_url = 'http://127.0.0.1:8000/api/rest/v1/%s'


def main():

    try:
        c_key, c_secret = get_consumer_keys()
    except ValueError:
        print >> sys.stderr, 'READABILITY_ACCESS_TOKEN and READABILITY_ACCESS_SECRET must be set.'
        sys.exit(1)

    token = get_access_token()

    rdd = readability.oauth(c_key, c_secret, token=token)

    url = raw_input('Enter a URL to bookmark: ')
    print url
    
    bookmark = rdd.add_bookmark(url=url)
    
    print bookmark


if __name__ == '__main__':
    main()
