try:
    import unittest2 as unittest
except ImportError:
    import unittest

from readability import ParserClient
from readability.clients import DEFAULT_PARSER_URL_TEMPLATE
from readability.core import required_from_env
from readability.tests import load_test_content

class ParserClientTest(unittest.TestCase):
    """
    Test case for the Parser Client
    """
    def setUp(self):
        self.parser_token = required_from_env('READABILITY_PARSER_TOKEN')
        self.parser_client = ParserClient(token=self.parser_token)
        self.test_url = 'https://en.wikipedia.org/wiki/Mark_Twain'

    def test_generate_url(self):
        """
        Test the clients ability to generate urls to endpoints.
        """
        # Test root resource
        expected_url = DEFAULT_PARSER_URL_TEMPLATE.format('')
        expected_url = '{}?token={}'.format(expected_url, self.parser_token)
        generated_url = self.parser_client._generate_url('')
        self.assertEqual(generated_url, expected_url)

        # Test parser resource
        expected_url = '{base_url}?token={token}&url=http%3A%2F%2Fwww.google.biz%2Fblog.html'.format(
            base_url=DEFAULT_PARSER_URL_TEMPLATE.format('parser'),
            token=self.parser_token)
        params = {'url': 'http://www.google.biz/blog.html'}
        generated_url = self.parser_client._generate_url(
            'parser', query_params=params)

        self.assertEqual(generated_url, expected_url)

    def test_get_root(self):
        """
        Test the client's ability to hit the root endpoint.
        """
        response = self.parser_client.get_root()

        expected_keys = set(['resources', ])
        self.assertEqual(set(response.json().keys()), expected_keys)

    def test_get_confidence(self):
        """
        Test the client's ability to hit the confidence endpoint.
        """
        # hit without an article_id or url. Should get an error.
        response = self.parser_client.get_confidence()
        self.assertEqual(response.status_code, 400)

        expected_keys = set(['url', 'confidence'])

        response = self.parser_client.get_confidence(url=self.test_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(set(response.json().keys()), expected_keys)
        # confidence for wikipedia should be over .5
        self.assertTrue(response.json()['confidence'] >= .5)

    def test_get_article_status(self):
        """
        Test the client's ability to hit the parser endpoint with a HEAD
        """
        # hit without an article_id or url. Should get an error.
        response = self.parser_client.get_confidence()
        self.assertEqual(response.status_code, 400)

        response = self.parser_client.get_article_status(url=self.test_url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers.get('x-article-status') is not None)
        self.assertTrue(response.headers.get('x-article-id') is not None)

    def test_get_article(self):
        """
        Test the client's ability to hit the parser endpoint with a GET
        """
        # test with incorrect params
        response = self.parser_client.get_article()
        self.assertEqual(response.status_code, 400)

        response = self.parser_client.get_article(url=self.test_url)
        self.assertEqual(response.status_code, 200)

        some_expected_keys = set(['content', 'domain', 'author', 'word_count',
            'title', 'total_pages'])
        self.assertTrue(
            some_expected_keys.issubset(set(response.json().keys())))

    def test_post_article_content(self):
        """
        Test the client's ability to hit the parser endpoint with a POST
        request.
        """
        content = load_test_content('content/test_post_content.html')
        url = 'http://thisisaurlthatdoesntmatterbutmustbepassedanyway.com/article.html'
        response = self.parser_client.post_article_content(content, url)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
