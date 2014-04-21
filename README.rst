.. image:: https://badge.fury.io/py/readability-api.png
    :target: http://badge.fury.io/py/readability-api

.. image:: https://travis-ci.org/arc90/python-readability-api.png
    :target: https://travis-ci.org/arc90/python-readability-api

readability-api
===============

readability-api is the official python client for Readability. It provides
access to both the Parser API and the Reader API.

The latest version can be installed via pip:

.. code-block:: bash
    
    pip install readability-api

Please refer to the `official docs
<https://readability-python-library.readthedocs.org/en/latest/>`_ for more
information and examples.


Tests
-----

Valid Parser, Reader, username, and password must be set as environment
variables before running the tests. This test suit runs agains the live
Readability API and also serves as integration tests. We recommend creating a
seperate testing user account on Readability to avoid disturbing your reading
list. **Note:** These tests do reset the bookmarks library of the provided user
when complete. They should *not* be run on your primary user account!

.. code-block:: bash

    # If you don't have it
    pip install tox

    export READABILITY_CONSUMER_KEY='...'
    export READABILITY_CONSUMER_SECRET='...'
    export READABILITY_PARSER_TOKEN='...'
    export READABILITY_USERNAME='...'
    export READABILITY_PASSWORD='...'

    tox


API Keys and Access
-------------------

Don't have Readability API keys? You can find them on `your Readability account
settings page <https://www.readability.com/account/api>`_.


Licensing
---------

The code for readability-api is licensed under the `MIT License
<http://opensource.org/licenses/MIT>`_
