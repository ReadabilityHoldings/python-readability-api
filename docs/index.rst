.. Readability API Python Library documentation master file, created by
   sphinx-quickstart on Tue May 28 14:41:33 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Readability API Python Library's documentation!
==========================================================

Release v\ |version|.


.. toctree::
   :maxdepth: 2

   clients


Installation
------------

The Readability package is hosted on `Github <https://github.com/arc90/python-readability-api>`_ and
can easily be installed using `pip <http://www.pip-installer.org/>`_.


    $ pip install readability-api


Reader API Client
-----------------

The `Reader API <https://www.readability.com/developers/api/reader>`_ client
requires four pieces of credential data. A consumer key and consumer
secret can be obtained from the
`Readability account page <https://www.readability.com/settings/account>`_. In
addition to consumer creds, a user's key and secret must also be used for
authentication.

Under the hood, the ``ReaderClient`` use the popular `requests <http://docs.python-requests.org/en/latest/>`_
library. The objects returned by the ``ReaderClient`` are instances
of ``requests.Response``.

Getting a user's favorite bookmarks is easy.

::

    from readability import ReaderClient
    rdb_client = ReaderClient('consumer_token', 'consumer_secret', 'user_key', 'user_secret')
    bookmarks_response = rdb_client.get_bookmarks(favorite=True)
    print bookmarks_response.json()

    >>> {'bookmarks': [{'user_id': 9999, 'read_percent': u'0.00', ... }

See :class:`readability.ReaderClient` docs for a complete list of
available functionality.


Parser API Client
-----------------

Authentication with the `Parser API <http://readability.com/developers/api/parser>`_
is simpler than the Reader API. All that's needed is a single token that can
be obtained from the
`Readability account page <http://www.readability.com/account/api>`_. With a
token, getting the parsed output for an article is easy.

Under the hood, the ``ParserClient`` use the popular `requests <http://docs.python-requests.org/en/latest/>`_
library. The objects returned by the ``ParserClient`` are instances
of ``requests.Response``.

::

   from readability import ParserClient
   parser_client = ParserClient('your_parser_token')
   parser_response = parser_client.get_article_content('http://www.some-web-page/blog.html')
   print parser_response.content['content']
   >>> {"content" <div class=\"article-text\">\n<p>I'm idling outside Diamante's, [snip] ...</p></div>", ... }

See :class:`readability.ParserClient` docs for a complete list of
available functionality.
