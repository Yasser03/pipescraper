import unittest
from unittest.mock import MagicMock, patch
from pipescraper import GoogleNewsFetcher, FetchGoogleNews

class TestGoogleNews(unittest.TestCase):
    
    @patch('newspaper.google_news.GoogleNewsSource')
    def test_fetcher(self, MockSource):
        # Mocking newspaper4k's GoogleNewsSource
        mock_instance = MockSource.return_value
        mock_instance.article_urls.return_value = [
            "https://test.com/article1",
            "https://test.com/article2"
        ]
        
        fetcher = GoogleNewsFetcher(country="US", period="1d", max_results=2)
        urls = fetcher.fetch_top_news()
        
        self.assertEqual(len(urls), 2)
        self.assertEqual(urls[0], "https://test.com/article1")
        MockSource.assert_called_once_with(country="US", period="1d", max_results=2)
        mock_instance.build.assert_called_once_with(top_news=True)

    @patch('pipescraper.core.GoogleNewsFetcher.fetch_top_news')
    def test_fetch_pipe(self, mock_fetch):
        mock_fetch.return_value = ["https://test.com/1", "https://test.com/2"]
        
        # Test basic execution
        pipe = FetchGoogleNews(max_results=2)
        results = pipe._execute()
        
        self.assertEqual(results, ["https://test.com/1", "https://test.com/2"])
        
        # Test pipe operator
        results = (None >> FetchGoogleNews(max_results=2))
        self.assertEqual(results, ["https://test.com/1", "https://test.com/2"])

if __name__ == '__main__':
    unittest.main()
