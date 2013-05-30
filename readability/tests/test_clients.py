# -*- coding: utf-8 -*-

from unittest import TestCase

from readability import xauth, ParserClient, ReaderClient
from readability.clients import DEFAULT_PARSER_URL_TEMPLATE
from readability.tests.settings import \
        CONSUMER_KEY, CONSUMER_SECRET, PARSER_TOKEN, PASSWORD, USERNAME


class ReaderClientNoBookmarkTest(TestCase):
    """Tests for the Readability ReaderClient class that need no bookmarks.

    """
    def setUp(self):
        """Need to get a token for each test.

        """
        token_pair = xauth(CONSUMER_KEY, CONSUMER_SECRET, USERNAME, PASSWORD)
        self.token_key = token_pair[0]
        self.token_secret = token_pair[1]

        self.base_client = ReaderClient(CONSUMER_KEY, CONSUMER_SECRET,
            self.token_key, self.token_secret)

    def test_get_article(self):
        """Test the `get_article` method.

        """
        article_id = 'lun3elns'
        response = self.base_client.get_article(article_id)
        self.assertEqual(response.status, 200)
        self.assertTrue(isinstance(response.content, dict))

        # spot check some keys
        some_expected_keys = set(['direction', 'title', 'url', 'excerpt',
            'content', 'processed', 'short_url', 'date_published'])
        keys_set = set(response.content.keys())
        self.assertTrue(some_expected_keys.issubset(keys_set))

    def test_get_article_404(self):
        """Try getting an article that doesn't exist.

        """
        article_id = 1
        response = self.base_client.get_article(article_id)
        self.assertEqual(response.status, 404)
        self.assertTrue(isinstance(response.content, dict))
        self.assertTrue('error_message' in response.content)

    def test_get_user(self):
        """Test getting user data

        """
        user_response = self.base_client.get_user()
        self.assertEqual(user_response.status, 200)
        some_expected_keys = set(['username', 'first_name', 'last_name',
            'date_joined', 'email_into_address'])
        received_keys = set(user_response.content.keys())
        self.assertTrue(some_expected_keys.issubset(received_keys))

    def _test_get_tags(self):
        """Test getting tags.

        """
        tag_response = self.base_client.get_tags()
        self.assertEqual(tag_response.status, 200)
        self.assertTrue('tags' in tag_response.content)
        self.assertTrue(len(tag_response.content['tags']) > 0)


class ReaderClientSingleBookmarkTest(TestCase):
    """Tests that only need one bookmark

    """
    def setUp(self):
        """Get a client and add a bookmark

        """
        token_pair = xauth(CONSUMER_KEY, CONSUMER_SECRET, USERNAME, PASSWORD)
        self.token_key = token_pair[0]
        self.token_secret = token_pair[1]

        self.base_client = ReaderClient(CONSUMER_KEY, CONSUMER_SECRET,
            self.token_key, self.token_secret)

        self.url = 'http://www.theatlantic.com/technology/archive/2013/01/the-never-before-told-story-of-the-worlds-first-computer-art-its-a-sexy-dame/267439/'
        add_response = self.base_client.add_bookmark(self.url)
        self.assertEqual(add_response.status, 202)

    def tearDown(self):
        """Remove all added bookmarks.

        """
        for bm in self.base_client.get_bookmarks().content['bookmarks']:
            del_response = self.base_client.delete_bookmark(bm['id'])
            self.assertEqual(del_response.status, 204)

    def test_get_bookmark(self):
        """Test getting one bookmark by id

        """
        # get a bookmark id
        bm_response = self.base_client.get_bookmarks()
        self.assertEqual(bm_response.status, 200)
        self.assertTrue(len(bm_response.content['bookmarks']) > 0)
        bookmark_id = bm_response.content['bookmarks'][0]['id']

        bm_response = self.base_client.get_bookmark(bookmark_id)
        self.assertEqual(bm_response.status, 200)
        some_expected_keys = set(['article', 'user_id', 'favorite', 'id'])
        received_keys = set(bm_response.content.keys())
        self.assertTrue(some_expected_keys.issubset(received_keys))


    def test_bookmark_tag_functionality(self):
        """Test adding, fetching and deleting tags on a bookmark.

        """
        # get a bookmark id
        bm_response = self.base_client.get_bookmarks()
        self.assertEqual(bm_response.status, 200)
        self.assertTrue(len(bm_response.content['bookmarks']) > 0)
        bookmark_id = bm_response.content['bookmarks'][0]['id']

        # test getting empty tags
        tag_response = self.base_client.get_bookmark_tags(bookmark_id)
        self.assertEqual(tag_response.status, 200)
        self.assertEqual(len(tag_response.content['tags']), 0)

        # test adding tags
        tags = ['tag', 'another tag']
        tag_string = ', '.join(tags)
        tag_add_response = \
            self.base_client.add_tags_to_bookmark(bookmark_id, tag_string)
        self.assertEqual(tag_add_response.status, 202)

        # re-fetch tags. should have 2
        retag_response = self.base_client.get_bookmark_tags(bookmark_id)
        self.assertEqual(retag_response.status, 200)
        self.assertEqual(len(retag_response.content['tags']), 2)
        for tag in retag_response.content['tags']:
            self.assertTrue(tag['text'] in tags)

        # test getting tags for user
        user_tag_resp = self.base_client.get_tags()
        self.assertEqual(user_tag_resp.status, 200)
        self.assertEqual(len(user_tag_resp.content['tags']), 2)
        for tag in user_tag_resp.content['tags']:
            self.assertTrue(tag['text'] in tags)

            # test getting a single tag while we're here
            single_tag_resp = self.base_client.get_tag(tag['id'])
            self.assertEqual(single_tag_resp.status, 200)
            self.assertTrue('applied_count' in single_tag_resp.content)
            self.assertTrue('id' in single_tag_resp.content)
            self.assertTrue('text' in single_tag_resp.content)

        # delete tags
        for tag in retag_response.content['tags']:
            del_response = self.base_client.delete_tag_from_bookmark(
                bookmark_id, tag['id'])
            self.assertEqual(del_response.status, 204)

        # check that tags are gone
        tag_response = self.base_client.get_bookmark_tags(bookmark_id)
        self.assertEqual(tag_response.status, 200)
        self.assertEqual(len(tag_response.content['tags']), 0)


class ReaderClientMultipleBookmarkTest(TestCase):
    """Tests for bookmark functionality

    """

    def setUp(self):
        """Add a few bookmarks.

        """
        token_pair = xauth(CONSUMER_KEY, CONSUMER_SECRET, USERNAME, PASSWORD)
        self.token_key = token_pair[0]
        self.token_secret = token_pair[1]

        self.base_client = ReaderClient(CONSUMER_KEY, CONSUMER_SECRET,
            self.token_key, self.token_secret)

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
            add_response = self.base_client.add_bookmark(url)
            self.assertEqual(add_response.status, 202)

        for url in self.favorite_urls:
            add_response = self.base_client.add_bookmark(url, favorite=True)
            self.assertEqual(add_response.status, 202)

        for url in self.archive_urls:
            add_response = self.base_client.add_bookmark(url, archive=True)
            self.assertEqual(add_response.status, 202)

    def test_get_bookmarks(self):
        """Test getting all bookmarks

        """
        bm_response = self.base_client.get_bookmarks()
        self.assertEqual(bm_response.status, 200)
        self.assertEqual(
            len(bm_response.content['bookmarks']), len(self.all_urls))

        # test favorite bookmarks
        bm_response = self.base_client.get_bookmarks(favorite=True)
        self.assertEqual(bm_response.status, 200)
        self.assertEqual(
            len(bm_response.content['bookmarks']), len(self.favorite_urls))
        for bm in bm_response.content['bookmarks']:
            self.assertTrue(bm['article']['url'] in self.favorite_urls)

        # test archive bookmarks
        bm_response = self.base_client.get_bookmarks(archive=True)
        self.assertEqual(bm_response.status, 200)
        self.assertEqual(
            len(bm_response.content['bookmarks']), len(self.archive_urls))
        for bm in bm_response.content['bookmarks']:
            self.assertTrue(bm['article']['url'] in self.archive_urls)

    def tearDown(self):
        """Remove all added bookmarks.

        """
        for bm in self.base_client.get_bookmarks().content['bookmarks']:
            del_response = self.base_client.delete_bookmark(bm['id'])
            self.assertEqual(del_response.status, 204)


class ParserClientTest(TestCase):
    """Test case for the Parser Client

    """

    def setUp(self):
        self.parser_client = ParserClient(PARSER_TOKEN)

    def test_generate_url(self):
        """Test the clients ability to generate urls to endpoints.

        """
        # test root resource
        expected_url = DEFAULT_PARSER_URL_TEMPLATE.format('')
        expected_url = '{0}?token={1}'.format(expected_url, PARSER_TOKEN)
        generated_url = self.parser_client._generate_url('')
        self.assertEqual(generated_url, expected_url)

        expected_url = DEFAULT_PARSER_URL_TEMPLATE.format('parser')
        params = {'url': 'http://www.beanis.biz/blog.html'}
        expected_url = '{0}?url=http%3A%2F%2Fwww.beanis.biz%2Fblog.html&token={1}'.format(
            expected_url, PARSER_TOKEN)

        generated_url = self.parser_client._generate_url(
            'parser', query_params=params)
        self.assertEqual(generated_url, expected_url)

    def test_get_root(self):
        """Test the client's ability to hit the root endpoint.

        """
        response = self.parser_client.get_root()

        expected_keys = set(['resources', ])
        self.assertEqual(set(response.content.keys()), expected_keys)


    def test_get_confidence(self):
        """Test the client's ability to hit the confidence endpoint.

        """
        # hit without an article_id or url. Should get an error.
        response = self.parser_client.get_confidence()
        self.assertEqual(response.status, 400)

        expected_keys = set(['url', 'confidence'])

        url = 'https://en.wikipedia.org/wiki/Mark_Twain'
        response = self.parser_client.get_confidence(url=url)
        self.assertEqual(response.status, 200)
        self.assertEqual(set(response.content.keys()), expected_keys)
        # confidence for wikipedia should be over .5
        self.assertTrue(response.content['confidence'] > .5)
