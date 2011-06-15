# -*- coding: utf-8 -*-

"""
readability.api
~~~~~~~~~~~~~~~

This module provies the core Readability API interface.
"""


import urllib
import urlparse

import oauth2
from decorator import decorator

from .config import settings
from .models import Bookmark, Article, Domain, Contribution, User
from .helpers import is_collection, to_python, to_api, get_scope


try:
    import json
except ImportError:
    import simplejson as json


@decorator
def admin_only(f, *args, **kwargs):
    """Admin-level API constraint decorator.

    Raises PermissionsError if settings.admin is not True.
    """

    if not settings.admin:
        func = get_scope(f, args)
        raise PermissionsError('%s is for Readability Admins only.' % (func,))

    return f(*args, **kwargs)


def raise_for_admin(status_code):
    if not settings.admin:
        raise PermissionsError('Resource for Readability Admins only.')


def raise_for_status(response):
    """Rasies appropriate errors for given HTTP Status, if neccesary."""

    status_code = int(response['status'])

    status_map = {
        400: BadRequestError,
        401: AuthenticationError,
        404: MissingError,
        403: PermissionsError,
        500: ServerError,
    }

    if status_code in status_map:
        raise status_map[status_code](response=response)


class ReadabilityCore(object):
    """The main Readability API interface."""

    def __init__(self):
        self.token = None
        self.username = None
        self.settings = settings


    def setup_client(self, token, consumer_key, consumer_secret):

        token = oauth2.Token(*token)
        consumer = oauth2.Consumer(consumer_key, consumer_secret)

        self.token = token
        self.client = oauth2.Client(consumer, token)

        self.username = self.get_me().username

        return True


    @property
    def token_tuple(self):
        """Returns serializable OAuth token."""

        token = dict(urlparse.parse_qsl(str(self.token)))
        return (token['oauth_token'], token['oauth_token_secret'])


    @staticmethod
    def _resource_serialize(o):
        """Returns JSON serialization of given object."""
        return json.dumps(o)


    @staticmethod
    def _resource_deserialize(s):
        """Returns dict deserialization of a given JSON string."""

        try:
            return json.loads(s)
        except ValueError:
            raise ResponseError('The API Response was not valid.')


    def _generate_url(self, resource, params):
        """Generates Readability API Resource URL."""

        if is_collection(resource):
            resource = map(str, resource)
            resource = '/'.join(resource)

        if params:
            resource += '?%s' % (urllib.urlencode(params))

        return settings.base_url % (resource,)


    def _get_http_resource(self, resource, params=None):
        """GETs HTTP Resource at given path."""

        url = self._generate_url(resource, params)

        if settings.verbose:
            settings.verbose.write('%s\n' % (url,))

        r, content = self.client.request(url, method='GET')
        raise_for_status(r)

        return content


    def _post_http_resource(self, resource, params=None):
        """POSTs HTTP Resource at given path."""

        url = self. _generate_url(resource, None)

        params = urllib.urlencode(params)
        r, content =  self.client.request(url, method='POST', body=params)
        raise_for_status(r)

        return r


    def _delete_http_resource(self, resource, params=None):
        """DELETEs HTTP Resource at given path."""

        url = self. _generate_url(resource, None)
        r, content =  self.client.request(url, method='DELETE')

        return r


    def _to_map(self, obj, iterable):
        """Maps given dict iterable to a given Resource object."""

        a = []

        for it in iterable:
            a.append(obj.new_from_dict(it, rdd=self))

        return a


    def _get_resources(self, key, obj, limit=None, **kwargs):
        """GETs resources of given path, maps them to objects, and
        handles paging.
        """

        if (limit is None) and ('per_page' not in kwargs):
            kwargs.update(per_page=50)
        else:
            kwargs.update(per_page=limit)

        items = []

        response = self._get_http_resource(key, params=kwargs)
        response = self._resource_deserialize(response)

        meta = response.get('meta')

        items.extend(self._to_map(obj, response.get(key)))

        if (len(items) < limit) or (limit is None):
            for i in range(meta.get('page')+1, meta.get('num_pages')+1):
                kwargs.update(page=i)
                if (len(items) < limit) or (limit is None):
                    response = self._get_http_resource(key, params=kwargs)
                    response = self._resource_deserialize(response)
                    items.extend(self._to_map(obj, response.get(key)))

        return items[:limit]


    def _get_resource(self, http_resource, obj, **kwargs):
        """GETs API Resource of given path."""

        item = self._get_http_resource(http_resource, params=kwargs)
        item = self._resource_deserialize(item)

        return obj.new_from_dict(item, rdd=self)


    def _post_resource(self, http_resource, **kwargs):
        """POSTs API Resource of given path."""

        r = self._post_http_resource(http_resource, params=kwargs)

        return r

    def _delete_resource(self, http_resource):
        """DELETEs API Resource of given path."""

        r = self._delete_http_resource(http_resource)

        if r['status'] in ('200', '204'):
            return True
        else:
            return False



class Readability(ReadabilityCore):
    """Main Readability API Endpoint for user consumption."""

    def __init__(self):
        super(Readability, self).__init__()


    @admin_only
    def get_articles(self, author=None, user=None, domain=None, limit=None, **filters):
        """Gets a list of articles."""

        filters.update(author=author, user=user, domain=domain)

        filters = to_api(
            filters,
            date_keys=(
                'added_since', 'added_until', 'published_since',
                'published_until'
            )
        )

        return self._get_resources('articles', Article, limit=limit, **filters)


    def get_article(self, id):
        """Gets Article of given ID."""

        return self._get_resource(('articles', id), Article)


    def get_bookmarks(self, archive=None, favorite=None, domain=None, limit=None, **filters):
        """Gets a list of bookmarks."""

        filters.update(
            archive=archive,
            favorite=archive,
            domain=domain,
        )

        filters = to_api(
            filters,
            date_keys = (
                'added_since', 'added_until', 'opened_since', 'opened_until',
                'archived_since', 'archived_until', 'favorited_since',
                'favorited_until', 'updated_since', 'updated_until'
            ),
            int_keys = ('archive', 'favorite')
        )

        return self._get_resources('bookmarks', Bookmark, limit=limit, **filters)


    @admin_only
    def get_bookmarks_by_user(self, username, **filters):
        """Gets bookmark of given user."""

        return self.get_bookmarks(user=username, **filters)


    def get_bookmark(self, id):
        """Gets bookmark of given ID."""

        return self._get_resource(('bookmarks', id), Bookmark)


    def get_contributions(self, limit=None, **filters):
        """Gets a list of contributions."""

        return self._get_resources('contributions', Contribution, limit=limit, params=filters)


    @admin_only
    def get_contributions_by_user(self, username, **filters):
        """Gets a list of contributions by given username."""

        return self.get_contributions(user=username, **filters)


    @admin_only
    def get_domains(self, domain=None, limit=None):
        """Gets a list of domains.

        .. warning::

            This Query is very slow.
        """

        filters = to_api(dict(domain=domain))

        return self._get_resources('domains', Domain, limit=limit, params=filters)


    @admin_only
    def get_domain(self, id):
        """Gets domain of given ID."""

        return self._get_resource(('domains', id), Domain)


    def get_me(self):
        """Returns logged in user."""

        return self._get_resource(('users', '_current'), User)


    @admin_only
    def get_users(self, limit=None, **filters):
        """Returns a list of users."""

        filters = to_api(filters, date_keys=('joined_since', 'joined_until'))

        return self._get_resources('users', User, limit=limit, params=filters)



    @admin_only
    def get_user(self, username='_current'):
        """Retrives a given user."""

        return self._get_resource(('users', username), User)


    def add_bookmark(self, url, favorite=False, archive=False):
        """Adds given bookmark."""

        r = self._post_resource(('bookmarks'), url=url, favorite=favorite, archive=archive)

        if r['status'] not in ('200','202'):
            raise ResponseError('')

        loc = r['location']
        resource = loc.split('/').pop()

        return self.get_bookmark(resource)


# ----------
# Exceptions
# ----------

class APIError(Exception):
    def __init__(self, msg=None, response=None):
        if msg is None:
            self.msg = self.__doc__
        else:
            self.msg = msg
            
        self.response = response

    def __str__(self):
        if self.response is not None:
            return "%s - response: %s" % (repr(self.msg), repr(self.response))
        else:
            return repr(self.msg)
        
class PermissionsError(APIError):
    """You do not have proper permission."""

class AuthenticationError(APIError):
    """Authentication failed."""

class ResponseError(APIError):
    """The API Response was unexpected."""

class MissingError(APIError):
    """The Resource does not exist."""

class BadRequestError(APIError):
    """The request could not be understood due to bad syntax. Check your request and try again."""
    
class ServerError(APIError):
    """The server encountered an error and was unable to complete your request."""