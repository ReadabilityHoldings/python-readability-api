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


import sys
from HTMLParser import HTMLParser

from ext import setup_rdd



class MLStripper(HTMLParser):
    """HTMLParser w/ overrides for stripping text out."""

    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ' '.join(self.fed)


def strip_tags(html):
    """A super low-tech and debatably irresponsible attempt to turn HTML
    into plain text."""

    s = MLStripper()
    s.feed(html)
    data = s.get_data()

    for s in ('\n\n\n\n\n', '\n\n\n\n', '\n\n\n', '\n', '\t'):

        data = data.replace(s, '')

    data = data.replace('  ', '')

    return data



def main():

    rdd = setup_rdd()

    bookmarks = rdd.get_me().bookmarks(limit=10)

    print 'Recent Bookmarks'
    print '----------------\n'

    for i, mark in enumerate(bookmarks):
        print '%01d: %s (%s)' % (i, mark.article.title, mark.article.domain)

    try:
        selection = raw_input('\nRead Article (0-9)? ')
        selection = int(selection)
        assert (selection < 10) and (selection >= 0)

    except (ValueError, AssertionError):
        print >> sys.stderr, '\nEnter a number within 0-9, if you don\'t mind.'

    except KeyboardInterrupt:
        print >> sys.stderr, '\nWell, fine.'
        sys.exit()

    article = bookmarks[selection].article
    article = rdd.get_article(article.id)

    print article.title

    print '-' * len(article.title) + '\n'

    print strip_tags(article.content)

if __name__ == '__main__':
    main()
