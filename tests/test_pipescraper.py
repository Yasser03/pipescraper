"""
Test suite for pipescraper.

This module contains unit tests and integration tests for the pipescraper package.
Run with: pytest tests/test_pipescraper.py -v
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from pipescraper import (
    FetchLinks,
    ExtractArticles,
    ToDataFrame,
    SaveAs,
    FilterArticles,
    LimitArticles,
    Deduplicate,
    Article,
    ArticleExtractor,
    LinkFetcher,
)
from pipescraper.utils import (
    is_valid_url,
    normalize_url,
    sanitize_text,
    get_domain,
)


# Fixtures

@pytest.fixture
def sample_article():
    """Create a sample Article object for testing."""
    return Article(
        url="https://example.com/article-1",
        source="example.com",
        title="Test Article",
        text="This is a test article with some content.",
        description="A test description",
        author="John Doe",
        date_published="2024-01-15",
        time_published="14:30:00",
        language="en",
        tags=["tech", "news"],
        image_url="https://example.com/image.jpg",
    )


@pytest.fixture
def sample_articles(sample_article):
    """Create a list of sample articles."""
    articles = [sample_article]
    
    # Add more articles
    for i in range(2, 5):
        articles.append(Article(
            url=f"https://example.com/article-{i}",
            source="example.com",
            title=f"Test Article {i}",
            text=f"Content for article {i}",
            author="Jane Smith" if i % 2 == 0 else "",
            date_published="2024-01-16",
            language="en",
        ))
    
    return articles


@pytest.fixture
def sample_html():
    """Sample HTML for testing link extraction."""
    return """
    <html>
        <head><title>News Site</title></head>
        <body>
            <a href="/article/2024/01/story-1">Story 1</a>
            <a href="/article/2024/01/story-2">Story 2</a>
            <a href="/category/tech">Tech Category</a>
            <a href="https://example.com/article/2024/01/story-3">Story 3</a>
            <a href="#top">Back to top</a>
        </body>
    </html>
    """


# Test Utils

class TestUtils:
    """Test utility functions."""
    
    def test_is_valid_url(self):
        """Test URL validation."""
        assert is_valid_url("https://example.com")
        assert is_valid_url("http://example.com/path")
        assert not is_valid_url("not a url")
        assert not is_valid_url("example.com")  # Missing scheme
    
    def test_normalize_url(self):
        """Test URL normalization."""
        assert normalize_url("HTTPS://EXAMPLE.COM/PATH") == "https://example.com/PATH"
        assert normalize_url("https://example.com/path/") == "https://example.com/path"
        assert normalize_url("https://example.com/#fragment") == "https://example.com/"
    
    def test_sanitize_text(self):
        """Test text sanitization."""
        assert sanitize_text("  Multiple   spaces  ") == "Multiple spaces"
        assert sanitize_text("Line1\n\nLine2") == "Line1 Line2"
        assert sanitize_text(None) == ""
    
    def test_get_domain(self):
        """Test domain extraction."""
        assert get_domain("https://example.com/path") == "example.com"
        assert get_domain("https://subdomain.example.com") == "subdomain.example.com"


# Test Core Classes

class TestArticle:
    """Test Article dataclass."""
    
    def test_article_creation(self, sample_article):
        """Test creating an Article."""
        assert sample_article.url == "https://example.com/article-1"
        assert sample_article.title == "Test Article"
        assert sample_article.author == "John Doe"
    
    def test_article_to_dict(self, sample_article):
        """Test converting Article to dictionary."""
        article_dict = sample_article.to_dict()
        
        assert isinstance(article_dict, dict)
        assert article_dict['url'] == sample_article.url
        assert article_dict['title'] == sample_article.title
        assert article_dict['tags'] == ['tech', 'news']


class TestLinkFetcher:
    """Test LinkFetcher class."""
    
    def test_can_fetch_no_robots(self):
        """Test fetching with robots.txt disabled."""
        fetcher = LinkFetcher(respect_robots=False)
        assert fetcher.can_fetch("https://example.com")
    
    def test_is_article_link(self):
        """Test article link detection heuristic."""
        fetcher = LinkFetcher()
        base_url = "https://example.com"
        
        # Should be article
        assert fetcher._is_article_link("https://example.com/article/2024/03/12/this-is-a-story", base_url)
        assert fetcher._is_article_link("https://example.com/news/breaking-news-about-the-world", base_url)
        
        # Should not be article
        assert not fetcher._is_article_link("https://example.com/category/tech", base_url)
        assert not fetcher._is_article_link("https://example.com/author/john", base_url)
        assert not fetcher._is_article_link("https://other-domain.com/article", base_url)
    
    @patch('requests.Session.get')
    def test_fetch_links(self, mock_get, sample_html):
        """Test fetching links from a page."""
        # Mock the response
        mock_response = Mock()
        mock_response.content = sample_html.encode()
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        fetcher = LinkFetcher(respect_robots=False, delay=0)
        links = fetcher.fetch_links("https://example.com")
        
        assert isinstance(links, list)
        assert len(links) > 0
        # Should filter out category and fragment links
        assert not any('/category/' in link for link in links)


class TestArticleExtractor:
    """Test ArticleExtractor class."""
    
    @patch('requests.Session.get')
    @patch('trafilatura.extract')
    @patch('trafilatura.extract_metadata')
    def test_extract(self, mock_metadata, mock_extract, mock_get):
        """Test article extraction."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.text = "<html><body>Article content</body></html>"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        # Mock trafilatura
        mock_extract.return_value = "Extracted text content"
        
        mock_meta = Mock()
        mock_meta.title = "Test Title"
        mock_meta.author = "Test Author"
        mock_meta.date = "2024-01-15"
        mock_meta.description = "Test description"
        mock_meta.language = "en"
        mock_meta.tags = []
        mock_meta.image = ""
        mock_metadata.return_value = mock_meta
        
        extractor = ArticleExtractor(delay=0, extract_time=False)
        article = extractor.extract("https://example.com/article")
        
        assert article is not None
        assert article.title == "Test Title"
        assert article.author == "Test Author"
        assert article.text == "Extracted text content"


# Test Pipe Operations

class TestPipes:
    """Test pipe verb classes."""
    
    def test_fetch_links_pipe(self):
        """Test FetchLinks pipe verb."""
        with patch('pipescraper.core.LinkFetcher.fetch_links') as mock_fetch:
            mock_fetch.return_value = ["https://example.com/article-1"]
            
            result = "https://example.com" >> FetchLinks()
            
            assert isinstance(result, list)
            assert len(result) > 0
    
    def test_extract_articles_pipe(self):
        """Test ExtractArticles pipe verb."""
        with patch('pipescraper.core.ArticleExtractor.extract_batch') as mock_extract:
            mock_article = Article(
                url="https://example.com/article",
                title="Test",
                text="Content"
            )
            mock_extract.return_value = [mock_article]
            
            urls = ["https://example.com/article"]
            result = urls >> ExtractArticles()
            
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], Article)
    
    def test_to_dataframe_pipe(self, sample_articles):
        """Test ToDataFrame pipe verb."""
        result = sample_articles >> ToDataFrame()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_articles)
        assert 'url' in result.columns
        assert 'title' in result.columns
    
    def test_to_dataframe_exclude_text(self, sample_articles):
        """Test ToDataFrame without text column."""
        result = sample_articles >> ToDataFrame(include_text=False)
        
        assert 'text' not in result.columns
    
    def test_save_as_pipe(self, sample_articles, tmp_path):
        """Test SaveAs pipe verb."""
        output_file = tmp_path / "test_output.csv"
        
        df = sample_articles >> ToDataFrame()
        result = df >> SaveAs(str(output_file))
        
        # Should return the DataFrame for chaining
        assert isinstance(result, pd.DataFrame)
        
        # File should exist
        assert output_file.exists()
        
        # Should be readable
        loaded_df = pd.read_csv(output_file)
        assert len(loaded_df) == len(sample_articles)
    
    def test_save_as_json(self, sample_articles, tmp_path):
        """Test SaveAs with JSON format."""
        output_file = tmp_path / "test_output.json"
        
        df = sample_articles >> ToDataFrame()
        df >> SaveAs(str(output_file))
        
        assert output_file.exists()
    
    def test_filter_articles_pipe(self, sample_articles):
        """Test FilterArticles pipe verb."""
        # Filter articles with authors
        result = sample_articles >> FilterArticles(lambda a: bool(a.author))
        
        assert isinstance(result, list)
        assert all(article.author for article in result)
        assert len(result) < len(sample_articles)
    
    def test_limit_articles_pipe(self, sample_articles):
        """Test LimitArticles pipe verb."""
        result = sample_articles >> LimitArticles(2)
        
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_deduplicate_pipe(self):
        """Test Deduplicate pipe verb."""
        # Create articles with duplicates
        articles = [
            Article(url="https://example.com/1", title="Article 1"),
            Article(url="https://example.com/2", title="Article 2"),
            Article(url="https://example.com/1", title="Article 1 Duplicate"),
        ]
        
        result = articles >> Deduplicate()
        
        assert len(result) == 2
        assert result[0].url == "https://example.com/1"
        assert result[1].url == "https://example.com/2"
    
    def test_chained_pipes(self, sample_articles):
        """Test chaining multiple pipe operations."""
        result = (sample_articles
                  >> FilterArticles(lambda a: True)
                  >> LimitArticles(3)
                  >> ToDataFrame())
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3


# Integration Tests

class TestIntegration:
    """Integration tests for complete workflows."""
    
    @patch('requests.Session.get')
    @patch('pipescraper.core.LinkFetcher.fetch_links')
    @patch('pipescraper.core.ArticleExtractor.extract_batch')
    def test_full_pipeline(self, mock_extract, mock_fetch, mock_get, tmp_path):
        """Test complete pipeline from URL to saved file."""
        # Mock link fetching
        mock_fetch.return_value = [
            "https://example.com/article-1",
            "https://example.com/article-2",
        ]
        
        # Mock article extraction
        mock_extract.return_value = [
            Article(url="https://example.com/article-1", title="Article 1", text="Content 1"),
            Article(url="https://example.com/article-2", title="Article 2", text="Content 2"),
        ]
        
        output_file = tmp_path / "output.csv"
        
        # Run full pipeline
        result = ("https://example.com"
                  >> FetchLinks(max_links=10)
                  >> ExtractArticles()
                  >> ToDataFrame()
                  >> SaveAs(str(output_file)))
        
        # Verify results
        assert output_file.exists()
        
        df = pd.read_csv(output_file)
        assert len(df) == 2
        assert "title" in df.columns


# Error Handling Tests

class TestErrorHandling:
    """Test error handling and edge cases."""
    
    def test_invalid_url(self):
        """Test handling of invalid URLs."""
        with pytest.raises(ValueError):
            "not-a-url" >> FetchLinks()
    
    def test_empty_article_list(self):
        """Test handling empty article list."""
        result = [] >> ToDataFrame()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0
    
    def test_unsupported_save_format(self, sample_articles):
        """Test unsupported file format."""
        df = sample_articles >> ToDataFrame()
        
        with pytest.raises(ValueError):
            df >> SaveAs("output.unsupported")
    
    def test_limit_validation(self):
        """Test LimitArticles validation."""
        with pytest.raises(ValueError):
            LimitArticles(0)
        
        with pytest.raises(ValueError):
            LimitArticles(-1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
