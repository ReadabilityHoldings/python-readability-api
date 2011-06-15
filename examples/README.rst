Readability Examples
====================

You need to set the following environment variables set:

``READABILITY_CONSUMER_KEY``
``READABILITY_CONSUMER_SECRET``

Example::

    export READABILITY_CONSUMER_KEY=test-account
    export READABILITY_CONSUMER_SECRET=BZ8WsJUrmLqRRqYr2h6dGWSUC5AP6Vhd


If you don't have a set of keys,
`request one <https://www.readability.com/contact>`_ from the Readability team.


Example Scripts
---------------

`login-xauth.py``
    This module requests your username and password, and fetches your
    OAuth tokens (via xAuth) for use by the other modules.

`login-oauth.py``
    This module opens an authorization window in your webbrowser, and
    fetches your OAuth tokens for use by the other modules.

``list-bookmarks.py``
    This module queries lists your bookmarks.


