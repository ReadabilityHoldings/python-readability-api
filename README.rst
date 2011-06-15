python-readability
==================

This module provides a reference implimentation for consuming the
Readability API.


You can use it to:

- Add/Remove Bookmarks
- List Articles
- View Contributions


Authentication options

- XAuth (API Keys + Username/Password)
- OAuth (API Keys + User Authorization)


Usage
-----


Authentication is simple::

    import readability

    token = readability.xauth('consumer-key', 'consumer-secret', 'username', 'password')
    rdd = readability.oauth('consumer-key', 'consumer-secret', token=token)


Get user info::

    >>> rdd.get_me()
    <user name="username">


List a users bookmarks::

    >>> rdd.get_bookmarks()
    [<bookmark "1">, <bookmark "3">, <bookmark "5">, <bookmark "7">]

    >>> for b in rdd.get_bookmarks()
    ...     print b.article.url


List a user's favorites::

    >>> rdd.get_bookmarks(favorite=True)
    [<bookmark "3">]


Save the OAuth Token for later::

    >>> rdd.token_tuple
    ('oauth-token', 'oauth-secret')



Install
-------

Installing python-readability is easy::

    $ pip install readability

Of, if you must::

    $ easy_install readability

But, you `really shouldn't do that
<http://www.pip-installer.org/en/latest/index.html#pip-compared-to-easy-install>`_.



License
-------

The MIT License::

    Copyright (C) 2011 by Readability, LLC

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

