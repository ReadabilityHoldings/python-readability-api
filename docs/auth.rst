Authentication
==============

.. |three-legged-twitter| raw:: html

    <a href="https://dev.twitter.com/oauth/3-legged" target="_blank">three-legged oAuth flow</a>

Authentication can be accomplised through either a |three-legged-twitter| or
via xAuth where a username and password are exchanged directly for a user token
and secret.

That token and secret is then used to sign requests on behalf of the user.  A
user's credentials should never be stored and are not needed. You should favor
a three legged auth flow if your application can support it. For testing
purposes, or for applications where a redirect flow is prohibitive, you can use
the xauth class to generate the token pair needed to sign Reader API requests.



Client Documentation
--------------------

.. autoclass:: readability.auth.xauth
    :members:
