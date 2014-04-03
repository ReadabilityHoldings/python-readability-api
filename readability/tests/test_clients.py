# -*- coding: utf-8 -*-

from unittest import TestCase

from readability import xauth, ParserClient, ReaderClient
from readability.clients import DEFAULT_PARSER_URL_TEMPLATE
from readability.tests.settings import \
        CONSUMER_KEY, CONSUMER_SECRET, PARSER_TOKEN, PASSWORD, USERNAME


class ReaderClientNoBookmarkTest(TestCase):
    """
    Tests for the Readability ReaderClient class that need no bookmarks.
    """
    def setUp(self):
        """
        Need to get a token for each test.
        """
        token_pair = xauth(CONSUMER_KEY, CONSUMER_SECRET, USERNAME, PASSWORD)
        self.token_key = token_pair[0]
        self.token_secret = token_pair[1]

        self.reader_client = ReaderClient(CONSUMER_KEY, CONSUMER_SECRET,
            self.token_key, self.token_secret)

    def test_get_article(self):
        """
        Test the `get_article` method.
        """
        article_id = 'lun3elns'
        response = self.reader_client.get_article(article_id)
        self.assertEqual(response.status, 200)
        self.assertTrue(isinstance(response.content, dict))

        # spot check some keys
        some_expected_keys = set(['direction', 'title', 'url', 'excerpt',
            'content', 'processed', 'short_url', 'date_published'])
        keys_set = set(response.content.keys())
        self.assertTrue(some_expected_keys.issubset(keys_set))

    def test_get_article_404(self):
        """
        Try getting an article that doesn't exist.
        """
        article_id = 1
        response = self.reader_client.get_article(article_id)
        self.assertEqual(response.status, 404)
        self.assertTrue(isinstance(response.content, dict))
        self.assertTrue('error_message' in response.content)

    def test_get_user(self):
        """
        Test getting user data
        """
        user_response = self.reader_client.get_user()
        self.assertEqual(user_response.status, 200)
        some_expected_keys = set(['username', 'first_name', 'last_name',
            'date_joined', 'email_into_address'])
        received_keys = set(user_response.content.keys())
        self.assertTrue(some_expected_keys.issubset(received_keys))

    def _test_get_tags(self):
        """
        Test getting tags.
        """
        tag_response = self.reader_client.get_tags()
        self.assertEqual(tag_response.status, 200)
        self.assertTrue('tags' in tag_response.content)
        self.assertTrue(len(tag_response.content['tags']) > 0)


class ReaderClientSingleBookmarkTest(TestCase):
    """
    Tests that only need one bookmark
    """
    def setUp(self):
        """
        Get a client and add a bookmark
        """
        token_pair = xauth(CONSUMER_KEY, CONSUMER_SECRET, USERNAME, PASSWORD)
        self.token_key = token_pair[0]
        self.token_secret = token_pair[1]

        self.reader_client = ReaderClient(CONSUMER_KEY, CONSUMER_SECRET,
            self.token_key, self.token_secret)

        self.url = 'http://www.theatlantic.com/technology/archive/2013/01/the-never-before-told-story-of-the-worlds-first-computer-art-its-a-sexy-dame/267439/'
        add_response = self.reader_client.add_bookmark(self.url)
        self.assertEqual(add_response.status, 202)

    def tearDown(self):
        """
        Remove all added bookmarks.
        """
        for bm in self.reader_client.get_bookmarks().content['bookmarks']:
            del_response = self.reader_client.delete_bookmark(bm['id'])
            self.assertEqual(del_response.status, 204)

    def test_get_bookmark(self):
        """
        Test getting one bookmark by id
        """
        bookmark_id = self._get_bookmark_data()['id']

        bm_response = self.reader_client.get_bookmark(bookmark_id)
        self.assertEqual(bm_response.status, 200)
        some_expected_keys = set(['article', 'user_id', 'favorite', 'id'])
        received_keys = set(bm_response.content.keys())
        self.assertTrue(some_expected_keys.issubset(received_keys))

    def test_archive_bookmark(self):
        """
        Test archiving a bookmark. The ``archive_bookmark`` method is just
        a convenient wrapper around the ``update_bookmark`` method but
        we'll go ahead and test it anyway.
        """
        bm_data = self._get_bookmark_data()

    def test_bookmark_tag_functionality(self):
        """
        Test adding, fetching and deleting tags on a bookmark.
        """
        bookmark_id = self._get_bookmark_data()['id']

        # test getting empty tags
        tag_response = self.reader_client.get_bookmark_tags(bookmark_id)
        self.assertEqual(tag_response.status, 200)
        self.assertEqual(len(tag_response.content['tags']), 0)

        # test adding tags
        tags = ['tag', 'another tag']
        tag_string = ', '.join(tags)
        tag_add_response = \
            self.reader_client.add_tags_to_bookmark(bookmark_id, tag_string)
        self.assertEqual(tag_add_response.status, 202)

        # re-fetch tags. should have 2
        retag_response = self.reader_client.get_bookmark_tags(bookmark_id)
        self.assertEqual(retag_response.status, 200)
        self.assertEqual(len(retag_response.content['tags']), 2)
        for tag in retag_response.content['tags']:
            self.assertTrue(tag['text'] in tags)

        # test getting tags for user
        user_tag_resp = self.reader_client.get_tags()
        self.assertEqual(user_tag_resp.status, 200)
        self.assertEqual(len(user_tag_resp.content['tags']), 2)
        for tag in user_tag_resp.content['tags']:
            self.assertTrue(tag['text'] in tags)

            # test getting a single tag while we're here
            single_tag_resp = self.reader_client.get_tag(tag['id'])
            self.assertEqual(single_tag_resp.status, 200)
            self.assertTrue('applied_count' in single_tag_resp.content)
            self.assertTrue('id' in single_tag_resp.content)
            self.assertTrue('text' in single_tag_resp.content)

        # delete tags
        for tag in retag_response.content['tags']:
            del_response = self.reader_client.delete_tag_from_bookmark(
                bookmark_id, tag['id'])
            self.assertEqual(del_response.status, 204)

        # check that tags are gone
        tag_response = self.reader_client.get_bookmark_tags(bookmark_id)
        self.assertEqual(tag_response.status, 200)
        self.assertEqual(len(tag_response.content['tags']), 0)

    def _get_bookmark_data(self):
        """
        Convenience method to get a single bookmark's data.
        """
        bm_response = self.reader_client.get_bookmarks()
        self.assertEqual(bm_response.status, 200)
        self.assertTrue(len(bm_response.content['bookmarks']) > 0)
        return bm_response.content['bookmarks'][0]


class ReaderClientMultipleBookmarkTest(TestCase):
    """
    Tests for bookmark functionality
    """
    def setUp(self):
        """
        Add a few bookmarks.
        """
        token_pair = xauth(CONSUMER_KEY, CONSUMER_SECRET, USERNAME, PASSWORD)
        self.token_key = token_pair[0]
        self.token_secret = token_pair[1]

        self.reader_client = ReaderClient(CONSUMER_KEY, CONSUMER_SECRET,
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
            add_response = self.reader_client.add_bookmark(url)
            self.assertEqual(add_response.status, 202)

        for url in self.favorite_urls:
            add_response = self.reader_client.add_bookmark(url, favorite=True)
            self.assertEqual(add_response.status, 202)

        for url in self.archive_urls:
            add_response = self.reader_client.add_bookmark(url, archive=True)
            self.assertEqual(add_response.status, 202)

    def test_get_bookmarks(self):
        """
        Test getting all bookmarks
        """
        bm_response = self.reader_client.get_bookmarks()
        self.assertEqual(bm_response.status, 200)
        self.assertEqual(
            len(bm_response.content['bookmarks']), len(self.all_urls))

        # test favorite bookmarks
        bm_response = self.reader_client.get_bookmarks(favorite=True)
        self.assertEqual(bm_response.status, 200)
        self.assertEqual(
            len(bm_response.content['bookmarks']), len(self.favorite_urls))
        for bm in bm_response.content['bookmarks']:
            self.assertTrue(bm['article']['url'] in self.favorite_urls)

        # test archive bookmarks
        bm_response = self.reader_client.get_bookmarks(archive=True)
        self.assertEqual(bm_response.status, 200)
        self.assertEqual(
            len(bm_response.content['bookmarks']), len(self.archive_urls))
        for bm in bm_response.content['bookmarks']:
            self.assertTrue(bm['article']['url'] in self.archive_urls)

    def tearDown(self):
        """
        Remove all added bookmarks.
        """
        for bm in self.reader_client.get_bookmarks().content['bookmarks']:
            del_response = self.reader_client.delete_bookmark(bm['id'])
            self.assertEqual(del_response.status, 204)


class ParserClientTest(TestCase):
    """
    Test case for the Parser Client
    """
    def setUp(self):
        self.parser_client = ParserClient(PARSER_TOKEN)
        self.test_url = 'https://en.wikipedia.org/wiki/Mark_Twain'

    def test_generate_url(self):
        """
        Test the clients ability to generate urls to endpoints.
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
        """
        Test the client's ability to hit the root endpoint.
        """
        response = self.parser_client.get_root()

        expected_keys = set(['resources', ])
        self.assertEqual(set(response.content.keys()), expected_keys)

    def test_get_confidence(self):
        """
        Test the client's ability to hit the confidence endpoint.
        """
        # hit without an article_id or url. Should get an error.
        response = self.parser_client.get_confidence()
        self.assertEqual(response.status, 400)

        expected_keys = set(['url', 'confidence'])

        response = self.parser_client.get_confidence(url=self.test_url)
        self.assertEqual(response.status, 200)
        self.assertEqual(set(response.content.keys()), expected_keys)
        # confidence for wikipedia should be over .5
        self.assertTrue(response.content['confidence'] >= .5)

    def test_get_article_status(self):
        """
        Test the client's ability to hit the parser endpoint with a HEAD
        """
        # hit without an article_id or url. Should get an error.
        response = self.parser_client.get_confidence()
        self.assertEqual(response.status, 400)

        response = self.parser_client.get_article_status(url=self.test_url)
        self.assertEqual(response.status, 200)
        self.assertTrue(response.get('x-article-status') is not None)
        self.assertTrue(response.get('x-article-id') is not None)

    def test_get_article_content(self):
        """
        Test the client's ability to hit the parser endpoint with a GET
        """
        # test with incorrect params
        response = self.parser_client.get_article_content()
        self.assertEqual(response.status, 400)

        response = self.parser_client.get_article_content(url=self.test_url)
        self.assertEqual(response.status, 200)

        some_expected_keys = set(['content', 'domain', 'author', 'word_count',
            'title', 'total_pages'])
        self.assertTrue(
            some_expected_keys.issubset(set(response.content.keys())))

    def test_post_article_content(self):
        """
        Test the client's ability to hit the parser endpoint with a POST
        request.
        """
        # I'm sorry...
        content = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml"><head><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <title>Readability v1 Parser API</title><style type="text/css">
                            body {
                                font-family: sans-serif;
                                font: 0.8em/1.4 Arial, sans-serif;
                                margin: 2em 6em;
                                width: 65em;
                            }
                            pre {
                                font-family: Courier, monospace;
                                font-weight: 500;
                                font-size: 0.8em;
                                background-color: #eef;
                                padding: 1em;
                            }
                            .methods {
                                background-color: #e4e4e4;
                                margin-top: .4em;
                                padding: .6em;
                            }
                            .methods h4 {
                                border-bottom: 1px solid #fff;
                                padding: .1em 0;
                                margin-bottom: .4em;
                                color: #0b3c97;
                                font-size: 1.1em;
                            }
                            .methods h6 {
                                color: #666;
                                text-transform: lowercase;
                                margin: .6em 0 .3em;
                            }
                            .resource {
                                margin-bottom: 2em;
                                margin-top: .4em;
                            }
                            .resource h3 {
                                margin-bottom: .4em;
                                font-size: 1.4em;
                                color: #ff5700;
                            }
                            h1 {
                                font-size: 2.5em;
                            }
                            h2 {
                                border-bottom: 1px solid black;
                                margin-top: 1em;
                                color: #666;
                                margin-bottom: 0.5em;
                                font-size: 2em;
                            }
                            h3 {
                                font-size: 1.75em;
                                margin: 0.6em 0;
                            }
                            h4 {
                                color: #666;
                                margin: 0;
                                padding: 0.3em 0;
                                border-bottom: 2px solid white;
                            }
                            h6 {
                                font-size: 1.1em;
                                color: #99a;
                                margin: 0.5em 0em 0.25em 0em;
                            }
                            dd {
                                margin-left: 1em;
                            }
                            tt {
                                font-size: 1.2em;
                            }
                            table {
                                margin-bottom: 0.5em;
                                width: 100%;
                                border-collapse: collapse;
                            }
                            th {
                                text-align: left;
                                font-weight: normal;
                                color: black;
                                border-bottom: 1px solid black;
                                padding: 3px 6px;
                            }
                            td {
                                padding: 3px 6px;
                                vertical-align: top;
                                background-color: f6f6ff;
                                font-size: 0.85em;
                            }
                            td p {
                                margin: 0px;
                            }
                            ul {
                                padding-left: 1.75em;
                            }
                            p + ul, p + ol, p + dl {
                                margin-top: 0em;
                            }
                            .optional {
                                font-weight: normal;
                                opacity: 0.75;
                            }
                        </style><link href="prettify/prettify.css" type="text/css" rel="stylesheet"></link><script type="text/javascript" src="prettify/prettify.js"></script></head><body onload="prettyPrint()"><h1>Readability v1 Parser API</h1>
                <section>
                    <h2 id="authentication">Authentication</h2>
                    <p>
                        Requests to the Parser API are not signed like an OAuth
                        request.  The Parser token is simply passed as a POST or GET
                        parameter depending on the request type. Be careful not to
                        reveal this token, requests directly to the Parser API should
                        not be made on the client device but rather proxied to keep the
                        API token secure.
                    </p>
                </section>

                <section>
                    <h2 id="quick-start">Quick Start</h2>
                    <p class="section-intro">
                                Here's how to pull an article's content from the Readability Parser API:
                    </p>
                    <h4>Request</h4>
                    <pre>GET /api/content/v1/parser?url=http://blog.readability.com/2011/02/step-up-be-heard-readability-ideas/&amp;token=1b830931777ac7c2ac954e9f0d67df437175e66e</pre>
                    <h4>Response</h4>
                    <pre>
        HTTP/1.0 200 OK
        {
            "content" &lt;div class=\"article-text\"&gt;\n&lt;p&gt;I'm idling outside Diamante's, [snip] ...&lt;/p&gt;&lt;/div&gt;",
            "domain": "www.gq.com",
            "author": "Rafi Kohan",
            "url": "http://www.gq.com/sports/profiles/201202/david-diamante-interview-cigar-lounge-brooklyn-new-jersey-nets?currentPage=all",
            "short_url": "http://rdd.me/g3jcb1sr",
            "title": "Blowing Smoke with Boxing's Big Voice",
            "excerpt": "I'm idling outside Diamante's, a cigar lounge in Fort Greene, waiting for David Diamante, and soon I smell him coming. It's late January but warm. A motorcycle growls down the Brooklyn side street,&amp;hellip;",
            "direction": "ltr",
            "word_count": 2892,
            "total_pages": 1,
            "date_published": null,
            "dek": "Announcer &lt;strong&gt;David Diamante&lt;/strong&gt;, the new voice of the New Jersey (soon Brooklyn) Nets, has been calling boxing matches for years. On the side, he owns a cigar lounge in the heart of Brooklyn. We talk with Diamante about his new gig and the fine art of cigars",
            "lead_image_url": "http://www.gq.com/images/entertainment/2012/02/david-diamante/diamante-628.jpg",
            "next_page_id": null,
            "rendered_pages": 1
        }
        </pre>
                </section>

                <section>
                    <h2 id="data-formats">Data Formats</h2>
                    <p>
                        All requests are, by default, provided as JSON. You may also pass "?format=xml" in the URL to convert this into XML data to be consumed.
                    </p>
                </section>

            <h3>Resources, Representations &amp; Errors</h3><ul><li><a href="#resources">Resources</a><ul><li><a href="#idp3728">https://readability.com/api/content/v1/</a></li><li><a href="#idp4080">https://readability.com/api/content/v1/parser</a></li><li><a href="#idp39744">https://readability.com/api/content/v1/confidence</a></li></ul></li><li><a href="#representations">Representations</a><ul><li><a href="#https://readability.com/api/content/v1#rootRepresentation">Example root representation. (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#articleRepresentation">Example article representation. (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#confidenceRepresentation">Example confidence representation. (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#confidenceRepresentationJsonp">Example confidence representation as jsonp. (application/json)</a></li></ul></li><li><a href="#faults">Errors</a><ul><li><a href="#https://readability.com/api/content/v1#error_400">400 Bad Request (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#error_401">401 Authorization Required (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#error_500">500 Internal Server Error (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#error_404">404 Not Found (application/json)</a></li></ul></li></ul><h2 id="resources">Resources</h2><div class="resource"><h3 id="idp3728">/</h3><h6>Methods</h6><div class="methods"><div class="method"><h4 id="idp5008">GET</h4>
                            Retrieve the base API URI - information about subresources.
                        <h6>request header parameters</h6><table><tr><th style="width: 25%">parameter</th><th style="width: 20%">value</th><th>description</th></tr><tr><td><p><strong>Authorization</strong></p></td><td><p><em><a href="" title=""></a></em><small> (required)</small></p></td><td></td></tr></table><p><em>available response representations:</em></p><ul><li><a href="#https://readability.com/api/content/v1#rootRepresentation">Example root representation. (application/json)</a></li></ul></div></div></div><div class="resource"><h3 id="idp4080">/parser?token<span class="optional">&amp;url</span><span class="optional">&amp;id</span><span class="optional">&amp;max_pages</span></h3><h6>Methods</h6><div class="methods"><div class="method"><h4 id="idp36384">GET</h4>
                            Parse an article
                        <h6>request query parameters</h6><table><tr><th style="width: 25%">parameter</th><th style="width: 20%">value</th><th>description</th></tr><tr><td><p><strong>token</strong></p></td><td><p><em><a href="http://www.w3.org/TR/xmlschema-2/#string">string</a></em><small> (required)</small></p></td><td></td></tr><tr><td><p><strong>url</strong></p></td><td><p><em><a href="http://www.w3.org/TR/xmlschema-2/#string">string</a></em></p></td><td>The URL of an article to return the content for.</td></tr><tr><td><p><strong>id</strong></p></td><td><p><em><a href="http://www.w3.org/TR/xmlschema-2/#string">string</a></em></p></td><td>The ID of an article to return the content for.</td></tr><tr><td><p><strong>max_pages</strong></p></td><td><p><em><a href="http://www.w3.org/TR/xmlschema-2/#integer">integer</a></em></p></td><td>The maximum number of pages to parse and combine. Default is 25.</td></tr></table><p><em>available response representations:</em></p><ul><li><a href="#https://readability.com/api/content/v1#articleRepresentation">Example article representation. (application/json)</a></li></ul><p><em>potential faults:</em></p><ul><li><a href="#https://readability.com/api/content/v1#error_400">400 Bad Request (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#error_401">401 Authorization Required (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#error_500">500 Internal Server Error (application/json)</a></li></ul></div><div class="method"><h4 id="idp63552">HEAD</h4>
                            <p>
                                Retrieve the Content Status of an article. This is useful if you want to save yourself from POSTing a large html document. You can do a HEAD request on the resource, and check for the status of the article in the X-Article-Status header. <strong>Additionally, if we've never seen the article before, we'll return a 404, which also means you should POST.</strong>
                            </p>
                        <h6>request query parameters</h6><table><tr><th style="width: 25%">parameter</th><th style="width: 20%">value</th><th>description</th></tr><tr><td><p><strong>token</strong></p></td><td><p><em><a href="http://www.w3.org/TR/xmlschema-2/#string">string</a></em><small> (required)</small></p></td><td></td></tr><tr><td><p><strong>url</strong></p></td><td><p><em><a href="http://www.w3.org/TR/xmlschema-2/#string">string</a></em></p></td><td>The URL of an article to check.</td></tr><tr><td><p><strong>id</strong></p></td><td><p><em><a href="http://www.w3.org/TR/xmlschema-2/#string">string</a></em></p></td><td>The ID of an article to check.</td></tr></table><h6>response header parameters</h6><table><tr><th style="width: 25%">parameter</th><th style="width: 20%">value</th><th>description</th></tr><tr><td><p><strong>X-Article-Id</strong></p></td><td><p><em><a href="http://www.w3.org/TR/xmlschema-2/#string">string</a></em></p></td><td>
                                <p>The ID of the article within Readablity.</p>
                            </td></tr><tr><td><p><strong>X-Article-Status</strong></p></td><td><p><em><a href="http://www.w3.org/TR/xmlschema-2/#string">string</a></em></p></td><td>
                                <p>The status of the content in Readability. One of:</p>
                                <dl>
                                <dt>INVALID</dt>
                                <dd>We were unable to parse this URL for some reason. <em>Recommendation: Fail</em></dd>
                                <dt>UNRETRIEVED</dt>
                                <dd>We know of this article, but have not yet retrieved its content, or the cache has expired. <em>Recommendation: POST content to us</em></dd>
                                <dt>PROVIDED_BY_USER</dt>
                                <dd>We have retrieved the content for this URL from at least one user. <em>Recommendation: POST content to us</em></dd>
                                <dt>VALIDATED_BY_USERS</dt>
                                <dd>We have retrieved the content for this URL from multiple users, and have validated it. <em>Recommendation: GET the content from us.</em></dd>
                                <dt>FETCHED</dt>
                                <dd>We fetched the content for this URL manually, and it has been cached. <em>Recommendation:GET the content from us.</em></dd>
                                </dl>
                            </td></tr></table><p><em>potential faults:</em></p><ul><li><a href="#https://readability.com/api/content/v1#error_400">400 Bad Request (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#error_401">401 Authorization Required (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#error_404">404 Not Found (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#error_500">500 Internal Server Error (application/json)</a></li></ul></div></div></div><div class="resource"><h3 id="idp39744">/confidence?url<span class="optional">&amp;callback</span></h3><h6>Methods</h6><div class="methods"><div class="method"><h4 id="idp89296">GET</h4>Detect the confidence with which Readability could parse a given URL. Does not require a token.<h6>request query parameters</h6><table><tr><th style="width: 25%">parameter</th><th style="width: 20%">value</th><th>description</th></tr><tr><td><p><strong>url</strong></p></td><td><p><em><a href="http://www.w3.org/TR/xmlschema-2/#string">string</a></em><small> (required)</small></p></td><td>The URL of an article to return the confidence for.</td></tr><tr><td><p><strong>callback</strong></p></td><td><p><em><a href="http://www.w3.org/TR/xmlschema-2/#string">string</a></em></p></td><td>The jsonp callback function name.</td></tr></table><p><em>available response representations:</em></p><ul><li><a href="#https://readability.com/api/content/v1#confidenceRepresentation">Example confidence representation. (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#confidenceRepresentationJsonp">Example confidence representation as jsonp. (application/json)</a></li></ul><p><em>potential faults:</em></p><ul><li><a href="#https://readability.com/api/content/v1#error_400">400 Bad Request (application/json)</a></li><li><a href="#https://readability.com/api/content/v1#error_500">500 Internal Server Error (application/json)</a></li></ul></div></div></div><h2 id="representations">Representations</h2><h3 id="https://readability.com/api/content/v1#rootRepresentation">Example root representation. (application/json)</h3>
                    <pre xmlns="http://research.sun.com/wadl/2006/10" class="prettyprint">
        {
            "resources": {
                "parser": {
                    "description": "The Content Parser Resource",
                    "href": "/api/content/v1/parser"
                }
            }
        }
                    </pre>
                <h3 id="https://readability.com/api/content/v1#articleRepresentation">Example article representation. (application/json)</h3>
                    <pre xmlns="http://research.sun.com/wadl/2006/10" class="prettyprint">
        {
            "content" &lt;div class=\"article-text\"&gt;\n&lt;p&gt;I'm idling outside Diamante's, [snip] ...&lt;/p&gt;&lt;/div&gt;",
            "domain": "www.gq.com",
            "author": "Rafi Kohan",
            "url": "http://www.gq.com/sports/profiles/201202/david-diamante-interview-cigar-lounge-brooklyn-new-jersey-nets?currentPage=all",
            "short_url": "http://rdd.me/g3jcb1sr",
            "title": "Blowing Smoke with Boxing's Big Voice",
            "excerpt": "I'm idling outside Diamante's, a cigar lounge in Fort Greene, waiting for David Diamante, and soon I smell him coming. It's late January but warm. A motorcycle growls down the Brooklyn side street,&amp;hellip;",
            "direction": "ltr",
            "word_count": 2892,
            "total_pages": 1,
            "date_published": null,
            "dek": "Announcer &lt;strong&gt;David Diamante&lt;/strong&gt;, the new voice of the New Jersey (soon Brooklyn) Nets, has been calling boxing matches for years. On the side, he owns a cigar lounge in the heart of Brooklyn. We talk with Diamante about his new gig and the fine art of cigars",
            "lead_image_url": "http://www.gq.com/images/entertainment/2012/02/david-diamante/diamante-628.jpg",
            "next_page_id": null,
            "rendered_pages": 1
        }

        </pre>
                <h3 id="https://readability.com/api/content/v1#confidenceRepresentation">Example confidence representation. (application/json)</h3>
                    <pre xmlns="http://research.sun.com/wadl/2006/10" class="prettyprint">
        {
            "url": "http://www.gq.com/article/12",
            "confidence": .7
        }

        </pre>
                <h3 id="https://readability.com/api/content/v1#confidenceRepresentationJsonp">Example confidence representation as jsonp. (application/json)</h3>
                    <pre xmlns="http://research.sun.com/wadl/2006/10" class="prettyprint">
        callback({
            "url": "http://www.gq.com/article/12",
            "confidence": .7
        });

        </pre>
                <h2 id="faults">Errors</h2><h3 id="https://readability.com/api/content/v1#error_400">400 Bad Request (application/json)</h3>
                    The server could not understand your request. Verify that request parameters (and content, if any) are valid.
                <h3 id="https://readability.com/api/content/v1#error_401">401 Authorization Required (application/json)</h3>
                    <p>
                        Authentication failed or was not provided. Verify that you have sent valid ixDirectory credentials via HTTP Basic.
                    </p>
                    <p>A 'Www-Authenticate' challenge header will be sent with this type of error response.</p>
                <h3 id="https://readability.com/api/content/v1#error_500">500 Internal Server Error (application/json)</h3>
                    An unknown error has occurred.
                <h3 id="https://readability.com/api/content/v1#error_404">404 Not Found (application/json)</h3>
                    The resource that you requested does not exist.
                </body></html>
        """
        url = 'http://readability.com/developers/api/parser#https://readability.com/api/content/v1#test_suite'
        response = self.parser_client.post_article_content(content, url)
        self.assertEqual(response.status, 200)
        # should have gotten back content that is shorter than original
        self.assertTrue(len(content) > len(response.content['content']))
