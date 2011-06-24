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

Once you have your consumer keys setup, run the following to get your
access tokens::

    $ ./login-xauth.py <username> <password>

"""

from ext import setup_rdd


def main():

    rdd = setup_rdd()

    bookmarks = rdd.get_me().bookmarks()

    for mark in bookmarks:
        print '- %s (%s)' % (mark.article.title, mark.article.domain)


if __name__ == '__main__':
    main()
