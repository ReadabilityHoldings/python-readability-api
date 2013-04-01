#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
add-bookmark.py
~~~~~~~~~~~~~~~~~

This module is an example of how to add a bookmark to a user's reading list.

"""

import sys

from readability import Client
from ext import get_consumer_keys, get_access_token


def main():

    try:
        c_key, c_secret = get_consumer_keys()
    except ValueError:
        print >> sys.stderr, 'READABILITY_ACCESS_TOKEN and READABILITY_ACCESS_SECRET must be set.'
        sys.exit(1)

    token = get_access_token()

    rdb_client = Client(c_key, c_secret, token=token)

    url = raw_input('Enter a URL to bookmark: ')
    print url

    bookmark = rdb_client.add_bookmark(url=url)
    print bookmark


if __name__ == '__main__':
    main()
