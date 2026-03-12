import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
from pipescraper.core import ArticleExtractor, Article

def test_newspaper4k_time_extraction():
    """Test that newspaper4k is used exclusively for time extraction."""
    url = "https://example.com/article"
    html = "<html><body>Content</body></html>"
    
    # Mock trafilatura to return basic metadata
    with patch('trafilatura.extract_metadata') as mock_trafilatura_meta, \
         patch('trafilatura.extract') as mock_trafilatura_extract, \
         patch('requests.Session.get') as mock_get:
        
        mock_get.return_value.text = html
        mock_get.return_value.status_code = 200
        
        mock_trafilatura_meta.return_value = MagicMock(
            title="Trafilatura Title",
            description="Trafilatura Desc",
            author="Trafilatura Author",
            date="2024-03-12",
            language="en",
            tags=[],
            image=None,
            sitename="Example",
            hostname="example.com",
            categories=[],
            pagetype="article"
        )
        mock_trafilatura_extract.return_value = "Article content"
        
        # Mock newspaper
        with patch('newspaper.Article', create=True) as mock_np_article_class:
            mock_np_article = MagicMock()
            mock_np_article_class.return_value = mock_np_article
            
            # Set a publish_date with time
            mock_np_article.publish_date = datetime(2024, 3, 12, 14, 30, 0)
            mock_np_article.title = "Newspaper Title" # Should be ignored
            mock_np_article.authors = ["Newspaper Author"] # Should be ignored
            
            extractor = ArticleExtractor(extract_time=True)
            article = extractor.extract(url)
            
            # Verify basics from trafilatura primarily, but updated by newspaper4k
            assert article.title == "Trafilatura Title"
            assert article.author == "Trafilatura Author"
            assert article.date_published == "2024-03-12" # Matches mock datetime
            
            # Verify time from newspaper4k
            assert article.time_published == "14:30:00"
            
            # Verify newspaper4k was called correctly
            mock_np_article_class.assert_called_once_with(url)
            mock_np_article.download.assert_called_once_with(input_html=html)
            mock_np_article.parse.assert_called_once()
            
            # Verify fallbacks are NOT used (Article title should still be Trafilatura's)
            assert article.title != "Newspaper Title"
            assert article.author != "Newspaper Author"

def test_newspaper4k_no_time_extraction():
    """Test that newspaper4k is NOT used when extract_time=False."""
    url = "https://example.com/article"
    
    with patch('trafilatura.extract_metadata') as mock_trafilatura_meta, \
         patch('trafilatura.extract') as mock_trafilatura_extract, \
         patch('requests.Session.get') as mock_get:
        
        mock_get.return_value.text = "html"
        mock_get.return_value.status_code = 200
        mock_trafilatura_meta.return_value = MagicMock(title="Title")
        mock_trafilatura_extract.return_value = "Content"
        
        with patch('newspaper.Article', create=True) as mock_np_article_class:
            extractor = ArticleExtractor(extract_time=False)
            article = extractor.extract(url)
            
            assert article.time_published == ""
            mock_np_article_class.assert_not_called()
