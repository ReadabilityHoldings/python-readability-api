Parser API Client
=================

The `Parser API
<http://readability.com/developers/api/parser>`_ is an API for programmatically
extracting content and metadata from html documents. Unlike the Reader API, the
Parser API does not require oAuth authentication but rather a single `token`
query parameter that must be used to sign every requests. You can find your
token by visiting `your Readability account settings page <https://www.readability.com/settings/account>`_.

This `token` can then be passed to the constructor or can be set via
environment variables.

.. code-block:: bash

    export READABILITY_PARSER_TOKEN='your parser token here'

.. code-block:: python

    from readability import ParserClient
    client = ParserClient(token='your parser token')

Under the hood, the `ParserClient` uses the popular `requests
<http://docs.python-requests.org/en/latest/>`_ library. The objects returned by
client calls are instances of `requests.Response
<http://docs.python-requests.org/en/latest/api/#requests.Response>`_.



Client Documentation
--------------------

.. autoclass:: readability.ParserClient
    :members:
