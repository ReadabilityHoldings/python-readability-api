# -*- coding: utf-8 -*-
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from readability import xauth, ReaderClient


class ReaderClientNoBookmarkTest(unittest.TestCase):
    """
    Tests for the Readability ReaderClient class that need no bookmarks.
    """
    def setUp(self):
        """
        Need to get a token for each test.

        """
        token_key, token_secret = xauth()
        self.reader_client = ReaderClient(token_key, token_secret)

    def test_get_article(self):
        """
        Test the `get_article` method.
        """
        article_id = 'orrspy2p'
        response = self.reader_client.get_article(article_id)
        self.assertEqual(response.status_code, 200)

        # spot check some keys
        some_expected_keys = set(['direction', 'title', 'url', 'excerpt',
            'content', 'processed', 'short_url', 'date_published'])
        keys_set = set(response.json().keys())
        self.assertTrue(some_expected_keys.issubset(keys_set))

    def test_get_article_404(self):
        """
        Try getting an article that doesn't exist.
        """
        article_id = 'antidisestablishmentarianism'
        response = self.reader_client.get_article(article_id)
        self.assertEqual(response.status_code, 404)

    def test_get_user(self):
        """
        Test getting user data
        """
        user_response = self.reader_client.get_user()
        self.assertEqual(user_response.status_code, 200)
        some_expected_keys = set(['username', 'first_name', 'last_name',
            'date_joined', 'email_into_address'])
        received_keys = set(user_response.json().keys())
        self.assertTrue(some_expected_keys.issubset(received_keys))

    def test_get_empty_tags(self):
        """
        Test getting an empty set of tags. Since there are no bookmarks
        present in this test, there should be no tags.
        """
        tag_response = self.reader_client.get_tags()
        self.assertEqual(tag_response.status_code, 200)
        response_json = tag_response.json()
        self.assertTrue('tags' in response_json)
        self.assertEqual(len(response_json['tags']), 0)


class ReaderClientSingleBookmarkTest(unittest.TestCase):
    """
    Tests that only need one bookmark
    """
    def setUp(self):
        """
        Get a client and add a bookmark
        """
        token_key, token_secret = xauth()
        self.reader_client = ReaderClient(token_key=token_key, token_secret=token_secret)
        self.url = 'http://www.theatlantic.com/technology/archive/2013/01/the-never-before-told-story-of-the-worlds-first-computer-art-its-a-sexy-dame/267439/'
        add_response = self.reader_client.add_bookmark(self.url)
        self.assertTrue(add_response.status_code in [201, 202])

    def tearDown(self):
        """
        Remove all added bookmarks.
        """
        for bm in self.reader_client.get_bookmarks().json()['bookmarks']:
            del_response = self.reader_client.delete_bookmark(bm['id'])
            self.assertEqual(del_response.status_code, 204)

    def test_get_bookmark(self):
        """
        Test getting one bookmark by id
        """
        bookmark_id = self._get_bookmark_data()['id']

        bm_response = self.reader_client.get_bookmark(bookmark_id)
        self.assertEqual(bm_response.status_code, 200)
        some_expected_keys = set(['article', 'user_id', 'favorite', 'id'])
        received_keys = set(bm_response.json().keys())
        self.assertTrue(some_expected_keys.issubset(received_keys))

    def test_bookmark_tag_functionality(self):
        """
        Test adding, fetching and deleting tags on a bookmark.
        """
        bookmark_id = self._get_bookmark_data()['id']

        # test getting empty tags
        tag_response = self.reader_client.get_bookmark_tags(bookmark_id)
        self.assertEqual(tag_response.status_code, 200)
        self.assertEqual(len(tag_response.json()['tags']), 0)

        # test adding tags
        tags = ['tag', 'another tag']
        tag_string = ', '.join(tags)
        tag_add_response = \
            self.reader_client.add_tags_to_bookmark(bookmark_id, tag_string)
        self.assertEqual(tag_add_response.status_code, 202)

        # re-fetch tags. should have 2
        retag_response = self.reader_client.get_bookmark_tags(bookmark_id)
        self.assertEqual(retag_response.status_code, 200)
        self.assertEqual(len(retag_response.json()['tags']), 2)
        for tag in retag_response.json()['tags']:
            self.assertTrue(tag['text'] in tags)

        # test getting tags for user
        user_tag_resp = self.reader_client.get_tags()
        self.assertEqual(user_tag_resp.status_code, 200)
        self.assertEqual(len(user_tag_resp.json()['tags']), 2)
        for tag in user_tag_resp.json()['tags']:
            self.assertTrue(tag['text'] in tags)

            # test getting a single tag while we're here
            single_tag_resp = self.reader_client.get_tag(tag['id'])
            self.assertEqual(single_tag_resp.status_code, 200)
            self.assertTrue('applied_count' in single_tag_resp.json())
            self.assertTrue('id' in single_tag_resp.json())
            self.assertTrue('text' in single_tag_resp.json())

        # delete tags
        for tag in retag_response.json()['tags']:
            del_response = self.reader_client.delete_tag_from_bookmark(
                bookmark_id, tag['id'])
            self.assertEqual(del_response.status_code, 204)

        # check that tags are gone
        tag_response = self.reader_client.get_bookmark_tags(bookmark_id)
        self.assertEqual(tag_response.status_code, 200)
        self.assertEqual(len(tag_response.json()['tags']), 0)

    def _get_bookmark_data(self):
        """
        Convenience method to get a single bookmark's data.
        """
        bm_response = self.reader_client.get_bookmarks()
        self.assertEqual(bm_response.status_code, 200)
        bm_response_json = bm_response.json()
        self.assertTrue(len(bm_response_json['bookmarks']) > 0)
        return bm_response_json['bookmarks'][0]


class ReaderClientMultipleBookmarkTest(unittest.TestCase):
    """
    Tests for bookmark functionality
    """
    def setUp(self):
        """
        Add a few bookmarks.
        """
        token_key, token_secret = xauth()
        self.reader_client = ReaderClient(token_key=token_key, token_secret=token_secret)

        self.urls = [
            'http://www.theatlantic.com/technology/archive/2013/01/the-never-before-told-story-of-the-worlds-first-computer-art-its-a-sexy-dame/267439/',
            'http://www.theatlantic.com/business/archive/2013/01/why-smart-poor-students-dont-apply-to-selective-colleges-and-how-to-fix-it/272490/',
        ]

        self.favorite_urls = [
            'http://www.theatlantic.com/sexes/archive/2013/01/the-lonely-existence-of-mel-feit-mens-rights-advocate/267413/',
            'http://www.theatlantic.com/technology/archive/2013/01/women-in-combat-an-idea-whose-time-has-come-aided-by-technology/272483/'
        ]

        self.archive_urls = [
            'http://www.theatlantic.com/business/archive/2013/01/what-economics-can-and-cant-tell-us-about-the-legacy-of-legal-abortion/267459/',
            'http://www.theatlantic.com/business/archive/2013/01/5-ways-to-understand-just-how-absurd-spains-26-unemployment-rate-is/272502/'
        ]

        self.all_urls = self.urls + self.favorite_urls + self.archive_urls

        for url in self.urls:
            response = self.reader_client.add_bookmark(url)
            self.assertTrue(response.status_code in [201, 202])

        for url in self.favorite_urls:
            response = self.reader_client.add_bookmark(url, favorite=True)
            self.assertTrue(response.status_code in [201, 202])

        for url in self.archive_urls:
            response = self.reader_client.add_bookmark(url, archive=True)
            self.assertTrue(response.status_code in [201, 202])

    def test_get_bookmarks(self):
        """
        Test getting all bookmarks
        """
        response = self.reader_client.get_bookmarks()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.json()['bookmarks']), len(self.all_urls))

        # test favorite bookmarks
        response = self.reader_client.get_bookmarks(favorite=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.json()['bookmarks']), len(self.favorite_urls))
        for bm in response.json()['bookmarks']:
            self.assertTrue(bm['article']['url'] in self.favorite_urls)

        # test archive bookmarks
        response = self.reader_client.get_bookmarks(archive=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.json()['bookmarks']), len(self.archive_urls))
        for bm in response.json()['bookmarks']:
            self.assertTrue(bm['article']['url'] in self.archive_urls)

    def tearDown(self):
        """
        Remove all added bookmarks.
        """
        for bm in self.reader_client.get_bookmarks().json()['bookmarks']:
            del_response = self.reader_client.delete_bookmark(bm['id'])
            self.assertEqual(del_response.status_code, 204)


if __name__ == '__main__':
    unittest.main(warnings='ignore')
