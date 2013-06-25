# -*- coding: utf-8 -*-

"""
readability.clients
~~~~~~~~~~~~~~~~~~~

This module provies a client for the Reader API.

"""

import json
import logging
import urllib

import oauth2
import httplib2

from .utils import filter_args_to_dict


logger = logging.getLogger(__name__)
DEFAULT_READER_URL_TEMPLATE = 'https://readability.com/api/rest/v1/{0}'
DEFAULT_PARSER_URL_TEMPLATE = 'https://readability.com/api/content/v1/{0}'
ACCEPTED_BOOKMARK_FILTERS = ['archive', 'favorite', 'domain', 'added_since'
    'added_until', 'opened_since', 'opened_until', 'archived_since'
    'archived_until', 'updated_since', 'updated_until', 'page', 'per_page',
    'only_deleted', 'tags']


class BaseClient(object):
    """A base class for Readability clients.

    """

    def _create_response(self, response, content):
        """Modify the httplib2.Repsonse object to return.

        Add two attributes to it:

        1) `raw_content` - this is the untouched content returned from the
        server.

        2) `content` - this is a serialized response using `json.loads`.

        If the response was an error of any kind, the reponse content
        will be:

        ::
            {'error_message': <message from server>}

        The above will also be ran through `json.loads`.

        :param response: Repsonse received from API
        :param content: Content received from API

        """
        response.raw_content = content
        try:
            content = json.loads(content)
        except ValueError:
            # didn't get json output. Assuming it's a string
            if response.status >= 400:
                content = {'error_message': content}
            else:
                content = {'message': content}
        response.content = content

        return response


class ReaderClient(BaseClient):
    """Client for interacting with the Readability Reader API.

    Docs can be found at `http://www.readability.com/developers/api/reader`.

    """

    def __init__(self, consumer_key, consumer_secret, token_key, token_secret,
        base_url_template=DEFAULT_READER_URL_TEMPLATE):
        """Initialize the ReadeClient.

        :param consumer_key: Reader API key
        :param consumer_secret: Reader API secret
        :param token_key: Readability user token key
        :param token_secret: Readability user token secret
        :param base_url_template (optional): Template used to build URL to
            which requests will be sent. This shouldn't need to be passed as the
            main purpose for it is testing environments that the user probably
            doesn't have access to (staging, local dev, etc).

        """

        self.base_url_template = base_url_template
        self.token = oauth2.Token(token_key, token_secret)
        self.consumer = oauth2.Consumer(consumer_key, consumer_secret)
        self.oauth_client = oauth2.Client(self.consumer, self.token)

    def get(self, url):
        """Make a HTTP GET request to the Reader API.

        :param url: url to which to make a GET request.

        """
        logger.debug('Making GET request to %s', url)
        return self._create_response(
            *self.oauth_client.request(url, method='GET'))

    def post(self, url, post_params=None):
        """Make a HTTP POST request ot the Reader API.

        :param url: url to which to make a POST request.
        :param post_params: parameters to be sent in the request's body.

        """
        params = urllib.urlencode(post_params)
        logger.debug('Making POST request to %s with body %s', url, params)
        return self._create_response(
            *self.oauth_client.request(url, method='POST', body=params))

    def delete(self, url):
        """Make a HTTP DELETE request ot the Readability API.

        :param url: The url to which to send a DELETE request.

        """
        logger.debug('Making DELETE request to %s', url)
        return self._create_response(
            *self.oauth_client.request(url, method='DELETE'))

    def _generate_url(self, resource, query_params=None):
        """Generate a Readability URL to the given resource.

        :param resource: the path to the resource that the request should
            go to.
        :param query_params (optional): a dict of query params that should
            be added to the url.

        """
        if query_params:
            resource = '{0}?{1}'.format(
                resource, urllib.urlencode(query_params))

        return self.base_url_template.format(resource)

    def get_article(self, article_id):
        """Get a single article represented by `article_id`.

        :param article_id: ID of the article to retrieve.

        """
        url = self._generate_url('articles/{0}'.format(article_id))
        return self.get(url)

    def get_bookmarks(self, **filters):
        """Get Bookmarks for the current user.

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
        """Get a single bookmark represented by `bookmark_id`.

        The requested bookmark must belong to the current user.

        :param bookmark_id: ID of the bookmark to retrieve.

        """
        url = self._generate_url('bookmarks/{0}'.format(bookmark_id))
        return self.get(url)

    def add_bookmark(self, url, favorite=False, archive=False):
        """Adds given bookmark.

        """

        rdb_url = self._generate_url('bookmarks')
        params = dict(url=url, favorite=int(favorite), archive=int(archive))
        return self.post(rdb_url, params)

    def delete_bookmark(self, bookmark_id):
        """Delete a single bookmark represented by `bookmark_id`.

        The requested bookmark must belong to the current user.

        :param bookmark_id: ID of the bookmark to delete.

        """
        url = self._generate_url('bookmarks/{0}'.format(bookmark_id))
        return self.delete(url)

    def get_bookmark_tags(self, bookmark_id):
        """Retrieve tags that have been applied to a bookmark.

        The requested bookmark must belong to the current user.

        :param bookmark_id: ID of the bookmark to delete.

        """
        url = self._generate_url('bookmarks/{0}/tags'.format(bookmark_id))
        return self.get(url)

    def add_tags_to_bookmark(self, bookmark_id, tags):
        """Add tags to to a bookmark.

        The identified bookmark must belong to the current user.

        :param bookmark_id: ID of the bookmark to delete.
        :param tags: Comma separated tags to be applied.

        """
        url = self._generate_url('bookmarks/{0}/tags'.format(bookmark_id))
        params = dict(tags=tags)
        return self.post(url, params)

    def delete_tag_from_bookmark(self, bookmark_id, tag_id):
        """Remove a single tag from a bookmark.

        The identified bookmark must belong to the current user.

        :param bookmark_id: ID of the bookmark to delete.

        """
        url = self._generate_url('bookmarks/{0}/tags/{1}'.format(
            bookmark_id, tag_id))
        return self.delete(url)

    def get_tag(self, tag_id):
        """Get a single tag represented by `tag_id`.

        The requested tag must belong to the current user.

        :param tag_id: ID fo the tag to retrieve.

        """
        url = self._generate_url('tags/{0}'.format(tag_id))
        return self.get(url)

    def get_tags(self):
        """Get all tags belonging to the current user.

        """
        url = self._generate_url('tags')
        return self.get(url)

    def get_user(self):
        """Retrives the current user.

        """
        url = self._generate_url('users/_current')
        return self.get(url)


class ParserClient(BaseClient):
    """Client for interacting with the Readability Parser API.

    Docs can be found at `http://www.readability.com/developers/api/parser`.

    """

    def __init__(self, token, base_url_template=DEFAULT_PARSER_URL_TEMPLATE):
        """Initialize client.

        :param token: parser API token.
        :param base_url_template (optional): Template used to build URL to
            which requests will be sent. This shouldn't need to be passed as the
            main purpose for it is testing environments that the user probably
            doesn't have access to (staging, local dev, etc).
        """
        logger.debug('Initializing ParserClient with base url template %s',
            base_url_template)

        self.token = token
        self.base_url_template = base_url_template


    def get(self, url):
        """Make an HTTP GET request to the Parser API.

        :param url: url to which to make the request

        """
        logger.debug('Making GET request to %s', url)
        http = httplib2.Http()
        return self._create_response(*http.request(url, 'GET'))

    def head(self, url):
        """Make an HTTP HEAD request to the Parser API.

        :param url: url to which to make the request

        """
        logger.debug('Making HEAD request to %s', url)
        http = httplib2.Http()
        return self._create_response(*http.request(url, 'HEAD'))

    def post(self, url, post_params=None):
        """Make an HTTP POST request to the Parser API.

        :param url: url to which to make the request
        :param post_params: POST data to send along. Expected to be a dict.

        """
        post_params['token'] = self.token
        params = urllib.urlencode(post_params)
        logger.debug('Making POST request to %s with body %s', url, params)
        http = httplib2.Http()
        return self._create_response(*http.request(url, 'POST', body=params))

    def _generate_url(self, resource, query_params=None):
        """Build the url to resource.

        :param resource: Name of the resource that is being called. Options are
        `''` (empty string) for root resource, `'parser'`, `'confidence'`.
        :param query_params: Data to be passed as query parameters.

        """
        if query_params:
            # extra & is for the token to be added
            resource = '{0}?{1}&'.format(
                resource, urllib.urlencode(query_params))
        else:
            # if we don't have query parameters, setup the url with the
            # resource name and question mark so that we can add the token
            # easier
            resource = '{0}?'.format(resource)

        # add token
        resource = '{0}token={1}'.format(resource, self.token)

        # apply base url template and return
        return self.base_url_template.format(resource)

    def get_root(self):
        """Send a GET request to the root resource of the Parser API.

        """
        url = self._generate_url('')
        return self.get(url)

    def get_article_content(self, url=None, article_id=None, max_pages=25):
        """Send a GET request to the `parser` endpoint of the parser API to get
        article content.

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
        """POST content to be parsed to the Parser API.

        Note: Even when POSTing content, a url must still be provided.

        :param content: the content to be parsed
        :param url: the url that represents the content
        :param max_pages (optional): the maximum number of pages to parse
            and combine. Default is 25.

        """
        params = {
            'doc': content,
            'url': url,
            'max_pages': max_pages
        }
        url = self._generate_url('parser')
        return self.post(url, post_params=params)

    def get_article_status(self, url=None, article_id=None):
        """Send a HEAD request to the `parser` endpoint to the parser API to
        get the articles status.

        Returned is a `httplib2.Response` object. The id and status for the
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
        """Send a GET request to the `confidence` endpoint of the Parser API.

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
