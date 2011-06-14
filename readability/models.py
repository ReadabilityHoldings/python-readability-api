# -*- coding: utf-8 -*-

"""
readability.models
~~~~~~~~~~~~~~~~~~

This module provides the core Readability API models.
"""

from .helpers import is_collection, to_python
from .config import settings



class BaseResource(object):
    """A Base BaseResource object."""

    def __init__(self):
        super(BaseResource, self).__init__()
        self._rdd = None

    def __dir__(self):
        d = self.__dict__.copy()
        try:
            del d['_rdd']
        except KeyError:
            pass

        return d.keys()



class Bookmark(BaseResource):
    """Bookmark API Model."""

    def __init__(self):
        self.id = None
        self.user_id = None
        self.read_percent = None
        self.date_updated = None
        self.favorite = None
        self.archive = None
        self.date_archived = None
        self.date_opened = None
        self.article = None


    def __repr__(self):
        return '<bookmark id="%s">' % (self.id,)


    @staticmethod
    def new_from_dict(d, rdd=None):

        b = to_python(
            obj=Bookmark(), in_dict=d,
            string_keys = (
                'id', 'user_id', 'read_percent', 'favorite', 'archive',
                'author',
            ),
            date_keys = ('date_updated', 'date_archived', 'date_opened'),
            object_map = {'article': Article},
            _rdd = rdd
        )

        return b


    def delete(self):
        """Deletes Bookmark."""
        return self._rdd._delete_resource(('bookmarks', self.id))


    def update(self):
        """Updates Bookmark."""

        args = to_api(
            dict(
                favorite=self.favorite,
                archive=self.archive,
                read_percent=self.read_percent,
            ),
            int_keys=('favorite', 'archive')
        )

        r = self._rdd._post_resource(('bookmarks', self.id), **args)

        return r



class Article(BaseResource):

    def __init__(self):
        self.id = None
        self.domain = None
        self.title = None
        self.url = None
        self.short_url = None
        self.author = None
        self.word_count = None
        self.content = None
        self.date_published = None
        self.next_page_href = None
        self.processed = None
        self.content_size = None


    def __repr__(self):
        return '<article id="%s">' % (self.id,)


    @staticmethod
    def new_from_dict(d, rdd=None):

        return to_python(
            obj=Article(), in_dict=d,
            string_keys = (
                'id', 'domain', 'title', 'url', 'short_url', 'author',
                'word_count', 'content', 'next_page_href', 'processed',
                'content_size'
            ),
            date_keys = ('date_published',),
            _rdd = rdd
        )



class Domain(BaseResource):

    def __init__(self):
        super(Domain, self).__init__()

        self.fqdn = None
        self.articles_ref = None


    def __repr__(self):
        return '<domain fqdn="%s">' % (self.fqdn,)


    @staticmethod
    def new_from_dict(d, rdd=None):

        return to_python(
            obj=Domain(), in_dict=d,
            string_keys = ('fqdn', 'articles_ref'),
            _rdd = rdd
        )


    def articles(self, **filters):
        """Returns Article list, filtered by Domain."""

        return self._rdd.get_articles(domain=self.fqdn, **filters)


    def contributions(self):
        """Returns Article list, filtered by Domain."""

        return self._rdd.get_contributions(domain=self.fqdn, **filters)



class Contribution(BaseResource):

    def __init__(self):
        super(Contribution, self).__init__()

        self.date = None
        self.contribution = None
        self.user = None
        self.domain = None
        self.num_bookmarks = None


    def __repr__(self):
        return '<contribution domain="%s">' % (self.domain,)


    @staticmethod
    def new_from_dict(d, rdd=None):

        return to_python(
            obj=Contribution(), in_dict=d,
            string_keys = ('contribution', 'user', 'domain', 'num_bookmarks'),
            date_keys = ('date'),
            _rdd = rdd
        )



class User(BaseResource):
    """User API Model."""

    def __init__(self):
        self.username = None
        self.first_name = None
        self.last_name = None
        self.date_joined = None


    def __repr__(self):
        return '<user name="%s">' % (self.username,)


    @staticmethod
    def new_from_dict(d, rdd=None):

        return to_python(
            obj=User(), in_dict=d,
            string_keys = ('username', 'first_name'),
            date_keys = ('date_joined',),
            _rdd=rdd
        )


    def bookmarks(self, **filters):
        """Returns Bookmark list, filtered by User."""

        if self.username == self._rdd.username:
            return self._rdd.get_bookmarks(user=self.username, **filters)
        else:
            return self._rdd.get_bookmarks_by_user(self.username, **filters)


    def contributions(self, **filters):
        """Returns Contributions list, filtered by User."""

        if self.username == self._rdd.username:
            return self._rdd.get_contributions(user=self.username, **filters)
        else:
            return self._rdd.get_contributions_by_user(self.username, **filters)




