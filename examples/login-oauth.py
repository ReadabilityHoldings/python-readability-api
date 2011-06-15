#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
login-oauth.py
~~~~~~~~~~~~~~

This module is an example of how to harness the Readability API w/ OAuth.

This module expects the following environment variables to be set:

- READABILITY_CONSUMER_KEY
- READABILITY_CONSUMER_SECRET

"""


import sys
import webbrowser


from ext import readability, get_consumer_keys



USAGE = """
Usage:

   $ ./login-oauth.py <username> <password>


The following environment variables must be set:

- READABILITY_CONSUMER_KEY
- READABILITY_CONSUMER_SECRET
"""

TEMPLATE = """
To use the other example modules, run the following:

  $ export READABILITY_ACCESS_TOKEN=%s
  $ export READABILITY_ACCESS_SECRET=%s
"""

RAW_TEMPLATE = 'export READABILITY_ACCESS_TOKEN=%s ; export READABILITY_ACCESS_SECRET=%s'



def get_oauth_pin(url):
    """Grabs credentials from arguments."""

    webbrowser.open(url)
    return raw_input('Authorization PIN? ')


def main():

    try:
        c_key, c_secret = get_consumer_keys()
    except ValueError:
        print >> sys.stderr, 'READABILITY_CONSUMER_KEY and READABILITY_CONSUMER_SECRET must be set.'
        sys.exit(1)



    try:
        rdd = readability.oauth(c_key, c_secret, callback=get_oauth_pin)
    except readability.api.AuthenticationError:
        print >> sys.stderr, '\nLogin failed. Invalid credentials.'
        sys.exit(77)

    if c_key and c_secret:
        print 'Login successful!'

    if '--raw' in sys.argv:
        print RAW_TEMPLATE % (rdd.token_tuple)
    else:
        print TEMPLATE % (rdd.token_tuple)


if __name__ == '__main__':
    main()