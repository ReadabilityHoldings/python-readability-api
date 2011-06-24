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

Once you have your consumer keys set up, run the following to get your
access tokens:

    $ ./login-xauth.py <username> <password>

"""

from ext import setup_rdd


def main():

    rdd = setup_rdd()

    bookmark_id = raw_input('Enter an ID of a bookmark to toggle favorite status for: ')
    bookmark = rdd.get_bookmark(bookmark_id)

    print "Original bookmark is: %s" % (bookmark,)

    bookmark.favorite = not bookmark.favorite
    bookmark.update()

    print "Bookmark is now: %s" % (bookmark,)


if __name__ == '__main__':
    main()
