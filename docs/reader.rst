Reader API Client
=================

.. |reader-docs| raw:: html

    <a href="https://www.readability.com/developers/api/reader" target="_blank">Reader API</a>

.. |account-settings-page| raw:: html

    <a href="https://www.readability.com/settings/account" target="_blank">your Readability account settings page</a>

The |reader-docs| client requires four pieces of credential data. A consumer
key and consumer secret can be obtained from |account-settings-page|. In
addition to client credentials, a user's token key and token secret must also
be used for authentication. For more information regarding auth, visit the
`Authentication <auth.html>`_ section of the docs.

Your client key and secret can be passed to the constructor directly or set via
environment variables:

.. code-block:: bash
    export READABILITY_CONSUMER_KEY='your consumer key'
    export READABILITY_CONSUMER_SECRET='your consumer secret'

Under the hood, the `ReaderClient` use the popular `requests
<http://docs.python-requests.org/en/latest/>`_ library. The objects returned by
the ``ReaderClient`` are instances of `requests.Response <http://docs.python-requests.org/en/latest/api/#requests.Response>`_.


Client Documentation
--------------------

.. autoclass:: readability.ReaderClient
    :members:
