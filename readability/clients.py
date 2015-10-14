# -*- coding: utf-8 -*-

"""
readability.clients
~~~~~~~~~~~~~~~~~~~

This module provies a client for the Reader API.

"""

import logging

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import requests

from requests_oauthlib import OAuth1Session

from readability.core import required_from_env
from readability.utils import filter_args_to_dict

logger = logging.getLogger(__name__)
DEFAULT_READER_URL_TEMPLATE = 'https://www.readability.com/api/rest/v1/{}'
DEFAULT_PARSER_URL_TEMPLATE = 'https://www.readability.com/api/content/v1/{}'
ACCEPTED_BOOKMARK_FILTERS = [
    'added_since',
    'added_until',
    'archive',
    'archived_since',
    'archived_until',
    'domain',
    'favorite',
    'only_deleted',
    'opened_since',
    'opened_until',
    'page',
    'per_page',
    'tags',
    'updated_since',
    'updated_until',
]



class ReaderClient(object):
    """
    Client for interacting with the Readability Reader API.

    Docs can be found at `http://www.readability.com/developers/api/reader`.
    """
    def __init__(self, token_key, token_secret,
        base_url_template=DEFAULT_READER_URL_TEMPLATE, **xargs):
        """
        Initialize the ReaderClient.

        :param consumer_key: Reader API key, otherwise read from READABILITY_CONSUMER_KEY.
        :param consumer_secret: Reader API secret, otherwise read from READABILITY_CONSUMER_SECRET.
        :param token_key: Readability user token key
        :param token_secret: Readability user token secret
        :param base_url_template (optional): Template used to build URL to
            which requests will be sent. This shouldn't need to be passed as the
            main purpose for it is testing environments that the user probably
            doesn't have access to (staging, local dev, etc).

        """
        consumer_key = xargs.get('consumer_key') or required_from_env('READABILITY_CONSUMER_KEY')
        consumer_secret = xargs.get('consumer_secret') or required_from_env('READABILITY_CONSUMER_SECRET')

        self.base_url_template = base_url_template
        self.oauth_session = OAuth1Session(consumer_key, consumer_secret, token_key, token_secret)

    def get(self, url):
        """
        Make a HTTP GET request to the Reader API.

        :param url: url to which to make a GET request.
        """
        logger.debug('Making GET request to %s', url)
        return self.oauth_session.get(url)

    def post(self, url, post_params=None):
        """
        Make a HTTP POST request to the Reader API.

        :param url: url to which to make a POST request.
        :param post_params: parameters to be sent in the request's body.
        """
        params = urlencode(post_params)
        logger.debug('Making POST request to %s with body %s', url, params)
        return self.oauth_session.post(url, data=params)

    def delete(self, url):
        """
        Make a HTTP DELETE request to the Readability API.

        :param url: The url to which to send a DELETE request.
        """
        logger.debug('Making DELETE request to %s', url)
        return self.oauth_session.delete(url)

    def _generate_url(self, resource, query_params=None):
        """
        Generate a Readability URL to the given resource.

        :param resource: the path to the resource that the request should
            go to.
        :param query_params (optional): a dict of query params that should
            be added to the url.
        """
        if query_params:
            resource = '{0}?{1}'.format(
                resource, urlencode(query_params))

        return self.base_url_template.format(resource)

    def get_article(self, article_id):
        """
        Get a single article represented by `article_id`.

        :param article_id: ID of the article to retrieve.
        """
        url = self._generate_url('articles/{0}'.format(article_id))
        return self.get(url)

    def get_bookmarks(self, **filters):
        """
        Get Bookmarks for the current user.

        Filters:

        :param archive: Filter Bookmarks returned by archived status.
        :param favorite: Filter Bookmarks returned by favorite status.
        :param domain: Filter Bookmarks returned by a domain.
        :param added_since: Filter bookmarks by date added (since this date).
        :param added_until: Filter bookmarks by date added (until this date).
        :param opened_since: Filter bookmarks by date opened (since this date).
        :param opened_until: Filter bookmarks by date opened (until this date).
        :param archived_since: Filter bookmarks by date archived (since this date.)
        :param archived_until: Filter bookmarks by date archived (until this date.)
        :param updated_since: Filter bookmarks by date updated (since this date.)
        :param updated_until: Filter bookmarks by date updated (until this date.)
        :param page: What page of results to return. Default is 1.
        :param per_page: How many results to return per page. Default is 20, max is 50.
        :param only_deleted: Return only bookmarks that this user has deleted.
        :param tags: Comma separated string of tags to filter bookmarks.
        """
        filter_dict = filter_args_to_dict(filters, ACCEPTED_BOOKMARK_FILTERS)
        url = self._generate_url('bookmarks', query_params=filter_dict)
        return self.get(url)

    def get_bookmark(self, bookmark_id):
        """
        Get a single bookmark represented by `bookmark_id`.

        The requested bookmark must belong to the current user.

        :param bookmark_id: ID of the bookmark to retrieve.
        """
        url = self._generate_url('bookmarks/{0}'.format(bookmark_id))
        return self.get(url)

    def add_bookmark(self, url, favorite=False, archive=False, allow_duplicates=True):
        """
        Adds given bookmark to the authenticated user.

        :param url: URL of the article to bookmark
        :param favorite: whether or not the bookmark should be favorited
        :param archive: whether or not the bookmark should be archived
        :param allow_duplicates: whether or not to allow duplicate bookmarks to
            be created for a given url
        """
        rdb_url = self._generate_url('bookmarks')
        params = {
            "url": url,
            "favorite": int(favorite),
            "archive": int(archive),
            "allow_duplicates": int(allow_duplicates)
        }
        return self.post(rdb_url, params)

    def update_bookmark(self, bookmark_id, favorite=None, archive=None, read_percent=None):
        """
        Updates given bookmark. The requested bookmark must belong to the
        current user.

        :param bookmark_id: ID of the bookmark to update.
        :param favorite (optional): Whether this article is favorited or not.
        :param archive (optional): Whether this article is archived or not.
        :param read_percent (optional): The read progress made in this article,
            where 1.0 means the bottom and 0.0 means the very top.
        """
        rdb_url = self._generate_url('bookmarks/{0}'.format(bookmark_id))
        params = {}
        if favorite is not None:
            params['favorite'] = 1 if favorite == True else 0
        if archive is not None:
            params['archive'] = 1 if archive == True else 0
        if read_percent is not None:
            try:
                params['read_percent'] = float(read_percent)
            except ValueError:
                pass
        return self.post(rdb_url, params)

    def favorite_bookmark(self, bookmark_id):
        """
        Favorites given bookmark. The requested bookmark must belong to the
        current user.

        :param bookmark_id: ID of the bookmark to favorite.
        """
        return self.update_bookmark(bookmark_id, favorite=True)

    def archive_bookmark(self, bookmark_id):
        """
        Archives given bookmark. The requested bookmark must belong to the
        current user.

        :param bookmark_id: ID of the bookmark to archive.
        """
        return self.update_bookmark(bookmark_id, archive=True)

    def set_read_percent_of_bookmark(self, bookmark_id, read_percent):
        """
        Set the read percentage of given bookmark. The requested bookmark must
        belong to the current user.

        :param bookmark_id: ID of the bookmark to update.
        :param read_percent: The read progress made in this article,
          where 1.0 means the bottom and 0.0 means the very top.
        """
        return self.update_bookmark(bookmark_id, read_percent=read_percent)

    def delete_bookmark(self, bookmark_id):
        """
        Delete a single bookmark represented by `bookmark_id`.

        The requested bookmark must belong to the current user.

        :param bookmark_id: ID of the bookmark to delete.
        """
        url = self._generate_url('bookmarks/{0}'.format(bookmark_id))
        return self.delete(url)

    def get_bookmark_tags(self, bookmark_id):
        """
        Retrieve tags that have been applied to a bookmark.

        The requested bookmark must belong to the current user.

        :param bookmark_id: ID of the bookmark to delete.
        """
        url = self._generate_url('bookmarks/{0}/tags'.format(bookmark_id))
        return self.get(url)

    def add_tags_to_bookmark(self, bookmark_id, tags):
        """
        Add tags to to a bookmark.

        The identified bookmark must belong to the current user.

        :param bookmark_id: ID of the bookmark to delete.
        :param tags: Comma separated tags to be applied.
        """
        url = self._generate_url('bookmarks/{0}/tags'.format(bookmark_id))
        params = dict(tags=tags)
        return self.post(url, params)

    def delete_tag_from_bookmark(self, bookmark_id, tag_id):
        """
        Remove a single tag from a bookmark.

        The identified bookmark must belong to the current user.

        :param bookmark_id: ID of the bookmark to delete.
        """
        url = self._generate_url('bookmarks/{0}/tags/{1}'.format(
            bookmark_id, tag_id))
        return self.delete(url)

    def get_tag(self, tag_id):
        """
        Get a single tag represented by `tag_id`.

        The requested tag must belong to the current user.

        :param tag_id: ID fo the tag to retrieve.
        """
        url = self._generate_url('tags/{0}'.format(tag_id))
        return self.get(url)

    def get_tags(self):
        """
        Get all tags belonging to the current user.
        """
        url = self._generate_url('tags')
        return self.get(url)

    def get_user(self):
        """
        Retrives the current user.
        """
        url = self._generate_url('users/_current')
        return self.get(url)


class ParserClient(object):
    """
    Client for interacting with the Readability Parser API.

    Docs can be found at `http://www.readability.com/developers/api/parser`.
    """
    def __init__(self, base_url_template=DEFAULT_PARSER_URL_TEMPLATE, **xargs):
        """
        Initialize client.

        :param token: parser API token, otherwise read from READABILITY_PARSER_TOKEN.
        :param base_url_template (optional): Template used to build URL to
            which requests will be sent. This shouldn't need to be passed as the
            main purpose for it is testing environments that the user probably
            doesn't have access to (staging, local dev, etc).
        """
        logger.debug('Initializing ParserClient with base url template %s',
            base_url_template)

        self.token = xargs.get('token', None) or required_from_env('READABILITY_PARSER_TOKEN')
        self.base_url_template = base_url_template

    def get(self, url):
        """
        Make an HTTP GET request to the Parser API.

        :param url: url to which to make the request
        """
        logger.debug('Making GET request to %s', url)
        return requests.get(url)

    def head(self, url):
        """
        Make an HTTP HEAD request to the Parser API.

        :param url: url to which to make the request
        """
        logger.debug('Making HEAD request to %s', url)
        return requests.head(url)

    def post(self, url, post_params=None):
        """
        Make an HTTP POST request to the Parser API.

        :param url: url to which to make the request
        :param post_params: POST data to send along. Expected to be a dict.
        """
        post_params['token'] = self.token
        params = urlencode(post_params)
        logger.debug('Making POST request to %s with body %s', url, params)
        return requests.post(url, data=params)

    def _generate_url(self, resource, query_params=None):
        """
        Build the url to resource.

        :param resource: Name of the resource that is being called. Options are
        `''` (empty string) for root resource, `'parser'`, `'confidence'`.
        :param query_params: Data to be passed as query parameters.
        """
        resource = '{resource}?token={token}'.format(resource=resource, token=self.token)
        if query_params:
            resource += "&{}".format(urlencode(query_params))
        return self.base_url_template.format(resource)

    def get_root(self):
        """
        Send a GET request to the root resource of the Parser API.
        """
        url = self._generate_url('')
        return self.get(url)

    def get_article(self, url=None, article_id=None, max_pages=25):
        """
        Send a GET request to the `parser` endpoint of the parser API to get
        back the representation of an article.

        The article can be identified by either a URL or an id that exists
        in Readability.

        Note that either the `url` or `article_id` param should be passed.

        :param url (optional): The url of an article whose content is wanted.
        :param article_id (optional): The id of an article in the Readability
            system whose content is wanted.
        :param max_pages: The maximum number of pages to parse and combine.
            The default is 25.
        """
        query_params = {}
        if url is not None:
            query_params['url'] = url
        if article_id is not None:
            query_params['article_id'] = article_id
        query_params['max_pages'] = max_pages
        url = self._generate_url('parser', query_params=query_params)
        return self.get(url)

    def post_article_content(self, content, url, max_pages=25):
        """
        POST content to be parsed to the Parser API.

        Note: Even when POSTing content, a url must still be provided.

        :param content: the content to be parsed
        :param url: the url that represents the content
        :param max_pages (optional): the maximum number of pages to parse
            and combine. Default is 25.
        """
        params = {
            'doc': content,
            'max_pages': max_pages
        }
        url = self._generate_url('parser', {"url": url})
        return self.post(url, post_params=params)

    def get_article_status(self, url=None, article_id=None):
        """
        Send a HEAD request to the `parser` endpoint to the parser API to
        get the articles status.

        Returned is a `requests.Response` object. The id and status for the
        article can be extracted from the `X-Article-Id` and `X-Article-Status`
        headers.

        Note that either the `url` or `article_id` param should be passed.

        :param url (optional): The url of an article whose content is wanted.
        :param article_id (optional): The id of an article in the Readability
            system whose content is wanted.
        """
        query_params = {}
        if url is not None:
            query_params['url'] = url
        if article_id is not None:
            query_params['article_id'] = article_id
        url = self._generate_url('parser', query_params=query_params)
        return self.head(url)

    def get_confidence(self, url=None, article_id=None):
        """
        Send a GET request to the `confidence` endpoint of the Parser API.

        Note that either the `url` or `article_id` param should be passed.

        :param url (optional): The url of an article whose content is wanted.
        :param article_id (optional): The id of an article in the Readability
            system whose content is wanted.
        """
        query_params = {}
        if url is not None:
            query_params['url'] = url
        if article_id is not None:
            query_params['article_id'] = article_id
        url = self._generate_url('confidence', query_params=query_params)
        return self.get(url)
