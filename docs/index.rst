Readability Python API
======================

.. |parser-docs| raw:: html

    <a href="https://www.readability.com/developers/api/parser" target="_blank">Parser</a>

.. |reader-docs| raw:: html

    <a href="https://www.readability.com/developers/api/reader" target="_blank">Reader</a>

.. |repo-link| raw:: html

    <a href="https://github.com/arc90/python-readability-api" target="_blank">Github</a>

.. |pypi-link| raw:: html

    <a href="https://pypi.python.org/pypi/readability-api/" target="_blank">PyPI</a>

Version |version|

The official Python client library for the Readability |parser-docs| and
|reader-docs| APIs.

Development of the readability-api package is hosted on |repo-link|. The
package itself is hosted on |pypi-link| and can easily be installed using pip.


Version 1.0.0 Notice
--------------------

Version 1.0 and up have fundamentally changed the objects returned by calls to
the API. The underlying `requests.Response
<http://docs.python-requests.org/en/latest/api/#requests.Response>`_ objects
are returned which greatly increases transparency and ease of development.

This is a departure from the 0.x releases which provided wrapped objects and
hid the http request mechanics. These releases also did not use the Requests
library. Version 1.0 also transitions to using |requests-oauthlib| for oAuth
support.

In addition, 1.x introduces python3 support (woohoo!)

.. |requests-oauthlib| raw:: html
    
    <a href="https://github.com/requests/requests-oauthlib" target="_blank">requests-oauthlib</a>


Installation
------------

.. code-block:: bash

    pip install readability-api


Examples
--------

Getting a user's favorite bookmarks is easy.

.. code-block:: python

    from readability import ReaderClient

    # If no client credentials are passed to ReaderClient's constructor, they
    # will be looked for in your environment variables 
    client = ReaderClient(token_key="a user's key", token_secret"a user's secret")
    bookmarks_response = client.get_bookmarks(favorite=True)

    print(bookmarks_response.json())
    >>> {'bookmarks': [{'user_id': 9999, 'read_percent': u'0.00', ... }

See :class:`readability.ReaderClient` docs for a complete list of
available functionality.


.. code-block:: python

   from readability import ParserClient

   parser_client = ParserClient(token='your_parser_token')
   parser_response = parser_client.get_article('http://paulgraham.com/altair.html')
   article = parser_response.json()

   print(article['title'])
   >>> "What Microsoft Is this the Altair Basic of?"

   print(article['content'])
   >>> "<div><p>February 2015<p>One of the most valuable exercises you can try if you ..."

See :class:`readability.ParserClient` docs for a complete list of
available functionality.


.. toctree::
    :hidden:

    Authentication <auth>
    ReaderClient <reader>
    ParserClient <parser>
