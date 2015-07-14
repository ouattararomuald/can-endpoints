#-*- coding: utf-8 -*-

import feedparser
import unittest

from can_api import is_rss_feed_valid


class CanApiTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_is_rss_feed_valid_should_success(self):
        rss = feedparser.FeedParserDict()
        rss['channel'] = feedparser.FeedParserDict()
        rss['channel']['title'] = None
        rss['channel']['link'] = None
        rss['channel']['description'] = None
        rss['channel']['image'] = feedparser.FeedParserDict()
        rss['channel']['image']['url'] = None
        rss['channel']['image']['title'] = None
        rss['channel']['image']['link'] = None
        rss['channel']['image']['width'] = None
        rss['channel']['image']['height'] = None
        rss['items'] = list()
        self.assertFalse(is_rss_feed_valid(rss))
        rss['items'] = [{'title': '', 'link': '', 'guid': ''},
                        {'title': '', 'link': '', 'guid': '', 'published_parsed': ''},
                        {'title': '', 'link': '', 'guid': '', 'published_parsed': ''}]
        self.assertFalse(is_rss_feed_valid(rss))
        rss['items'] = [{'title': '', 'link': '', 'guid': '', 'published_parsed': ''},
                        {'title': '', 'link': '', 'guid': '', 'published_parsed': ''},
                        {'title': '', 'link': '', 'guid': '', 'published_parsed': ''}]
        self.assertTrue(is_rss_feed_valid(rss))

    def test_is_rss_feed_valid_should_failed(self):
        rss = feedparser.FeedParserDict()
        rss['channel'] = feedparser.FeedParserDict()
        rss['channel']['link'] = None
        rss['channel']['description'] = None
        rss['channel']['image'] = feedparser.FeedParserDict()
        rss['channel']['image']['url'] = None
        rss['channel']['image']['title'] = None
        rss['channel']['image']['link'] = None
        rss['channel']['image']['width'] = None
        rss['channel']['image']['height'] = None
        self.assertFalse(is_rss_feed_valid(rss))
        rss['channel']['title'] = None
        rss['items'] = [{'title': '', 'link': '', 'guid': ''},
                        {'title': '', 'link': '', 'guid': '', 'published_parsed': ''},
                        {'title': '', 'link': '', 'guid': '', 'published_parsed': ''}]
        self.assertFalse(is_rss_feed_valid(rss))

if __name__ == '__main__':
    unittest.main()