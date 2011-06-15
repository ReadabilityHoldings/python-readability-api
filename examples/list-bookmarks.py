#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
list-bookmarks.py
~~~~~~~~~~~~~~~~~

This module is an example of how to harness the Readability API w/ oAuth.

This module expects the following environment variables to be set:

- READABILITY_CONSUMER_KEY
- READABILITY_CONSUMER_SECRET
- READABILITY_ACCESS_TOKEN
- READABILITY_ACCESS_SECRET

Once you have your consumer keys setup, run the following to get your OAuth
tokens::

    $ ./login-xauth.py <username> <password>

"""


import sys

from ext import readability
from ext import get_consumer_keys, get_access_token



def main():

    try:
        c_key, c_secret = get_consumer_keys()
    except ValueError:
        print >> sys.stderr, 'READABILITY_ACCESS_TOKEN and READABILITY_ACCESS_SECRET must be set.'
        sys.exit(1)

    token = get_access_token()

    rdd = readability.oauth(c_key, c_secret, token=token)

    # print rdd.get_bookmarks(user='kreitz')
    bookmarks = rdd.get_me().bookmarks()

    for mark in bookmarks:
        print '- %s (%s)' % (mark.article.title, mark.article.domain)


if __name__ == '__main__':
    main()
