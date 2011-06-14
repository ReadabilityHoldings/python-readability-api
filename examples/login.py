#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
login.py
~~~~~~~~

This module is an example of how to harness the Readability API w/ xAuth.

This module expects the following environment variables to be set:

- READABILITY_CONSUMER_KEY
- READABILITY_CONSUMER_SECRET

"""


import sys

from ext import readability, get_consumer_keys



USAGE = """
Usage:

   $ ./login.py <username> <password>


The following environment variables must be set:

- READABILITY_CONSUMER_KEY
- READABILITY_CONSUMER_SECRET
"""

TEMPLATE = """
To use the other example modules, run the following:

  $ export READABILITY_OAUTH_TOKEN=%s
  $ export READABILITY_OAUTH_SECRET=%s
"""



def get_credentials():
    """Grabs credentials from arguments."""

    if len(sys.argv) < 3:
        print 'Credentials needed.'
        print >> sys.stderr, USAGE
        sys.exit(1)

    return sys.argv[1:3]


def main():

    user, passwd = get_credentials()
    try:
        c_key, c_secret = get_consumer_keys()
    except ValueError:
        print >> sys.stderr, 'READABILITY_OAUTH_TOKEN and READABILITY_OAUTH_SECRET must be set.'



    try:
        o_token, o_secret = readability.xauth(c_key, c_secret, user, passwd)
    except readability.api.AuthenticationError:
        print >> sys.stderr, '\nLogin failed. Invalid credentials.'
        sys.exit(77)

    if c_key and c_secret:
        print 'Login successful!'

    print TEMPLATE % (o_token, o_secret)


if __name__ == '__main__':
    main()