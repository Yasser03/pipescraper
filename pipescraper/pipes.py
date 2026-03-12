"""
Pipeable verb classes for pipescraper.

This module implements the natural language pipe syntax using the >> operator,
inspired by pipeframe and pipeplotly. Each verb class implements __rrshift__
to enable chaining operations.

Example:
    >>> ("https://news.site.com" >> 
    ...  FetchLinks() >> 
    ...  ExtractArticles() >> 
    ...  ToDataFrame() >> 
    ...  SaveAs("output.csv"))
    
    >>> # With PipeFrame integration
    >>> from pipeframe import select, filter, arrange
    >>> ("https://news.site.com" >> 
    ...  FetchLinks() >> 
    ...  ExtractArticles() >> 
    ...  ToPipeFrame() >>
    ...  select('title', 'author', 'date_published') >>
    ...  filter(lambda df: df['author'].notna()) >>
    ...  arrange('date_published', ascending=False) >>
    ...  SaveAs("articles.csv"))
"""

import logging
from typing import List, Optional, Union, Callable, Any
import pandas as pd

from pipescraper.core import Article, ArticleExtractor, LinkFetcher, GoogleNewsFetcher
from pipescraper.utils import is_valid_url
from pipescraper.pipeframe_integration import (
    articles_to_pipeframe,
    is_pipeframe,
    to_pipeframe,
    check_pipeframe_available,
    PIPEFRAME_AVAILABLE,
)

logger = logging.getLogger(__name__)


class PipeBase:
    """
    Base class for pipeable operations.
    
    All pipe verbs inherit from this class to enable the >> operator.
    """
    
    def __rrshift__(self, left):
        """
        Enable the >> operator for chaining.
        
        Args:
            left: Input from the left side of >> (can be data or another pipe)
            
        Returns:
            Result of the pipe operation
        """
        if isinstance(left, PipeBase):
            # If the left side is a producer or a previous pipe stage, 
            # execute it with None (producers should handle None)
            return self._execute(left._execute(None))
        return self._execute(left)
    
    def __call__(self, left):
        """
        Enable calling the pipe object directly (required by PipeFrame).
        
        Args:
            left: Input data
            
        Returns:
            Result of the pipe operation
        """
        return self._execute(left)
    
    def _execute(self, data):
        """
        Execute the pipe operation. Must be implemented by subclasses.
        
        Args:
            data: Input data
            
        Returns:
            Transformed data
        """
        raise NotImplementedError("Subclasses must implement _execute()")


class FetchLinks(PipeBase):
    """
    Fetch article links from a base URL.
    
    This verb accepts a URL string and returns a list of article URLs found
    on that page.
    
    Args:
        max_links: Maximum number of links to fetch (None for unlimited)
        respect_robots: Whether to respect robots.txt
        user_agent: User agent string for requests
        timeout: Request timeout in seconds
        delay: Delay between requests in seconds
    
    Example:
        >>> links = "https://news.site.com" >> FetchLinks(max_links=50)
    """
    
    def __init__(
        self,
        max_links: Optional[int] = None,
        respect_robots: bool = True,
        user_agent: str = "pipescraper/0.1.0",
        timeout: int = 10,
        delay: float = 0.05,
        print_url: bool = False,
    ):
        self.max_links = max_links
        self.respect_robots = respect_robots
        self.user_agent = user_agent
        self.timeout = timeout
        self.delay = delay
        self.print_url = print_url
    
    def _execute(self, data: str) -> List[str]:
        """
        Execute link fetching.
        
        Args:
            data: Base URL to scrape
            
        Returns:
            List of article URLs
        """
        if not isinstance(data, str):
            raise TypeError(f"FetchLinks expects a URL string, got {type(data)}")
        
        if not is_valid_url(data):
            raise ValueError(f"Invalid URL: {data}")
        
        fetcher = LinkFetcher(
            respect_robots=self.respect_robots,
            user_agent=self.user_agent,
            timeout=self.timeout,
            delay=self.delay,
            print_url=self.print_url,
        )
        
        links = fetcher.fetch_links(data, max_links=self.max_links)
        
        if self.print_url and links:
            print(f"Fetched {len(links)} links from {data}:")
            for i, link in enumerate(links[:5]):
                print(f"  {i+1}. {link}")
            if len(links) > 5:
                print(f"  ... and {len(links)-5} more")
                
        return links


class FetchGoogleNews(PipeBase):
    """
    Fetch article links from Google News.
    
    This verb produces a list of article URLs from Google News top stories.
    It can be used as the start of a pipeline.
    
    Args:
        country: Country code (e.g., "US", "GB")
        period: Time period (e.g., "1h", "1d", "7d")
        max_results: Maximum number of results to fetch
        search: Keywords or sentences to search for
    """
    
    def __init__(
        self,
        country: str = "US",
        period: str = "1d",
        max_results: int = 10,
        search: Optional[Union[str, List[str]]] = None,
        print_url: bool = False,
    ):
        """Initialize the FetchGoogleNews pipe."""
        self.country = country
        self.period = period
        self.max_results = max_results
        self.search = search
        self.print_url = print_url
        
    def _execute(self, data=None):
        """
        Execute the Google News fetcher.
        
        Args:
            data: Ignored, as this is typically the start of a pipe.
            
        Returns:
            List of Google News article URLs
        """
        fetcher = GoogleNewsFetcher(
            country=self.country,
            period=self.period,
            max_results=self.max_results,
            search=self.search,
            print_url=self.print_url
        )
        urls = fetcher.fetch_top_news()
        
        if self.print_url and urls:
            print(f"Fetched {len(urls)} URLs from Google News:")
            for i, url in enumerate(urls[:5]): # Print first 5 to avoid clutter
                print(f"  {i+1}. {url}")
            if len(urls) > 5:
                print(f"  ... and {len(urls)-5} more")
        
        return urls


class ExtractArticles(PipeBase):
    """
    Extract article metadata from URLs.
    
    This verb accepts a list of URLs and returns a list of Article objects
    with extracted metadata.
    
    Args:
        timeout: Request timeout in seconds
        delay: Delay between article extractions
        extract_time: Whether to extract publication date and time using newspaper4k
        user_agent: User agent for requests
        skip_errors: Whether to skip failed extractions (True) or raise (False)
    
    Example:
        >>> articles = urls >> ExtractArticles(delay=2.0)
    """
    
    def __init__(
        self,
        timeout: int = 10,
        delay: float = 0.1,
        extract_time: bool = True,
        user_agent: str = "pipescraper/0.1.0",
        skip_errors: bool = True,
        workers: Optional[int] = None,
        print_url: bool = False,
    ):
        """
        Initialize the ExtractArticles verb.
        
        Args:
            timeout: Request timeout in seconds
            delay: Delay between article extractions
            extract_time: Whether to extract date and time using newspaper4k (default: True)
            user_agent: User agent for requests
            skip_errors: Whether to skip URLs that fail to extract
            workers: Number of parallel workers (default: None, let OS decide)
            print_url: Whether to show detailed output
        """
        self.timeout = timeout
        self.delay = delay
        self.extract_time = extract_time
        self.user_agent = user_agent
        self.skip_errors = skip_errors
        self.workers = workers
        self.print_url = print_url
    
    def _execute(self, data: Union[str, List[str]]) -> List[Article]:
        """
        Execute article extraction.
        
        Args:
            data: Single URL or list of URLs
            
        Returns:
            List of extracted Article objects
        """
        if isinstance(data, str):
            urls = [data]
        else:
            urls = data
        
        if not isinstance(urls, list):
            raise TypeError(f"ExtractArticles expects URL(s), got {type(data)}")
        
        extractor = ArticleExtractor(
            timeout=self.timeout,
            delay=self.delay,
            extract_time=self.extract_time,
            user_agent=self.user_agent,
            print_url=self.print_url,
        )
        
        return extractor.extract_batch(urls, max_workers=self.workers)


class ToDataFrame(PipeBase):
    """
    Convert articles to a pandas DataFrame.
    
    This verb accepts a list of Article objects and returns a structured
    pandas DataFrame with all metadata fields as columns.
    
    Args:
        include_text: Whether to include full article text (can be large)
        print_url: Whether to show detailed output
    
    Example:
        >>> df = articles >> ToDataFrame(include_text=False)
    """
    
    def __init__(self, include_text: bool = True, print_url: bool = False):
        self.include_text = include_text
        self.print_url = print_url
    
    def _execute(self, data: List[Article]) -> pd.DataFrame:
        """
        Execute DataFrame conversion.
        
        Args:
            data: List of Article objects
            
        Returns:
            pandas DataFrame with article metadata
        """
        if not isinstance(data, list):
            raise TypeError(f"ToDataFrame expects list of articles, got {type(data)}")
        
        # Define standard columns based on Article.to_dict()
        columns = [
            'url', 'source', 'title', 'text', 'description', 
            'author', 'date_published', 'time_published', 
            'language', 'tags', 'image_url'
        ]
        
        if not data:
            logger.warning("Empty article list, returning empty DataFrame with schema")
            return pd.DataFrame(columns=columns)
        
        # Convert articles to dictionaries
        records = [article.to_dict() for article in data]
        
        # Create DataFrame
        df = pd.DataFrame(records)
        
        # Ensure all standard columns exist (in case some articles were missing fields)
        for col in columns:
            if col not in df.columns:
                df[col] = None
        
        # Reorder to match standard column order
        df = df[columns]
        
        # Optionally remove text column to reduce size
        if not self.include_text and 'text' in df.columns:
            df = df.drop(columns=['text'])
        
        if self.print_url:
            logger.info(f"Created DataFrame with {len(df)} articles")
        return df


class ToPipeFrame(PipeBase):
    """
    Convert articles to a PipeFrame DataFrame.
    
    This verb accepts a list of Article objects and returns a PipeFrame
    DataFrame with all pipeframe verb capabilities enabled.
    
    PipeFrame enables dplyr-style data manipulation with verbs like:
    - select(), drop(), rename()
    - filter(), arrange(), distinct()
    - mutate(), transmute()
    - group_by(), summarize()
    - head(), tail(), sample()
    
    Args:
        include_text: Whether to include full article text (can be large)
    
    Example:
        >>> from pipeframe import select, filter, arrange
        >>> pf = (articles >> 
        ...       ToPipeFrame() >>
        ...       select('title', 'author', 'date_published') >>
        ...       filter(lambda df: df['author'].notna()) >>
        ...       arrange('date_published', ascending=False))
    
    Raises:
        ImportError: If pipeframe is not installed
    """
    
    def __init__(self, include_text: bool = True, print_url: bool = False):
        self.include_text = include_text
        self.print_url = print_url
    
    def _execute(self, data: List[Article]):
        """
        Execute PipeFrame conversion.
        
        Args:
            data: List of Article objects
            
        Returns:
            PipeFrame DataFrame with article metadata
            
        Raises:
            ImportError: If pipeframe is not installed
        """
        if not isinstance(data, list):
            raise TypeError(f"ToPipeFrame expects list of articles, got {type(data)}")
        
        if not PIPEFRAME_AVAILABLE:
            raise ImportError(
                "PipeFrame is not installed. Install it with: pip install pipeframe\n"
                "Alternatively, use ToDataFrame() for standard pandas DataFrame."
            )
        
        pf = articles_to_pipeframe(data, include_text=self.include_text)
        
        if self.print_url:
            logger.info(f"Created PipeFrame with {len(pf)} articles")
        return pf


class SaveAs(PipeBase):
    """
    Save DataFrame to file.
    
    This verb accepts a DataFrame and saves it to the specified file format.
    Supports CSV, JSON, Excel, and Parquet.
    
    Args:
        filepath: Output file path (extension determines format)
        index: Whether to write row index
        **kwargs: Additional arguments passed to pandas save method
    
    Example:
        >>> df >> SaveAs("articles.csv")
        >>> df >> SaveAs("articles.xlsx", index=False)
    """
    
    def __init__(self, filepath: str, index: bool = False, print_url: bool = False, **kwargs):
        self.filepath = filepath
        self.index = index
        self.print_url = print_url
        self.kwargs = kwargs
    
    def _execute(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Execute file saving.
        
        Args:
            data: DataFrame to save
            
        Returns:
            The same DataFrame (for further chaining)
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError(f"SaveAs expects DataFrame, got {type(data)}")
        
        # Determine format from extension
        filepath_lower = self.filepath.lower()
        
        if filepath_lower.endswith('.csv'):
            data.to_csv(self.filepath, index=self.index, **self.kwargs)
        elif filepath_lower.endswith('.json'):
            data.to_json(self.filepath, orient='records', **self.kwargs)
        elif filepath_lower.endswith(('.xlsx', '.xls')):
            data.to_excel(self.filepath, index=self.index, **self.kwargs)
        elif filepath_lower.endswith('.parquet'):
            data.to_parquet(self.filepath, index=self.index, **self.kwargs)
        else:
            raise ValueError(f"Unsupported file format: {self.filepath}")
        
        if self.print_url:
            logger.info(f"Saved {len(data)} articles to {self.filepath}")
        return data


class FilterArticles(PipeBase):
    """
    Filter articles based on a condition.
    
    This verb accepts a list of Articles or URLs and returns filtered results
    based on the provided filter function.
    
    Args:
        condition: Function that takes an Article and returns bool
    
    Example:
        >>> # Filter for articles with authors
        >>> articles >> FilterArticles(lambda a: bool(a.author))
        >>> # Filter by language
        >>> articles >> FilterArticles(lambda a: a.language == 'en')
    """
    
    def __init__(self, condition: Callable[[Article], bool], print_url: bool = False):
        self.condition = condition
        self.print_url = print_url
    
    def _execute(self, data: Union[List[Article], pd.DataFrame, Any]) -> Any:
        """
        Execute filtering.
        
        Args:
            data: List of articles, pandas DataFrame, or PipeFrame to filter
            
        Returns:
            Filtered data (same type as input)
        """
        if isinstance(data, list):
            filtered = [article for article in data if self.condition(article)]
            if self.print_url:
                logger.info(f"Filtered {len(data)} articles to {len(filtered)}")
            return filtered
        
        if isinstance(data, pd.DataFrame) or is_pipeframe(data):
            # Apply row-wise if a DataFrame or PipeFrame is passed
            is_pf = is_pipeframe(data)
            df = data._data if is_pf else data
            
            # Apply condition to each row
            try:
                # Try applying to the whole DF if it's a vector-ready condition
                filtered_df = df[self.condition(df)]
            except Exception:
                # Fallback to row-wise apply
                filtered_df = df[df.apply(self.condition, axis=1)]
                
            if self.print_url:
                logger.info(f"Filtered {len(df)} rows to {len(filtered_df)}")
            return type(data)(filtered_df) if is_pf else filtered_df
            
        raise TypeError(f"FilterArticles expects list or DataFrame, got {type(data)}")


class LimitArticles(PipeBase):
    """
    Limit the number of articles.
    
    This verb accepts a list of Articles or URLs and returns only the first N items.
    
    Args:
        n: Number of articles to keep
    
    Example:
        >>> articles >> LimitArticles(10)
    """
    
    def __init__(self, n: int, print_url: bool = False):
        if n < 1:
            raise ValueError("Limit must be at least 1")
        self.n = n
        self.print_url = print_url
    
    def _execute(self, data: Union[List[Any], pd.DataFrame, Any]) -> Any:
        """
        Execute limiting.
        
        Args:
            data: List of articles or DataFrame
            
        Returns:
            Limited data
        """
        if isinstance(data, list):
            limited = data[:self.n]
            if self.print_url:
                logger.info(f"Limited {len(data)} articles to {len(limited)}")
            return limited
            
        if isinstance(data, pd.DataFrame) or is_pipeframe(data):
            limited_df = data.head(self.n)
            if self.print_url:
                logger.info(f"Limited {len(data)} rows to {len(limited_df)}")
            return limited_df
            
        raise TypeError(f"LimitArticles expects list or DataFrame, got {type(data)}")


class WithDelay(PipeBase):
    """
    Add delay to article extraction.
    
    This is a utility verb that modifies the delay parameter for the
    next ExtractArticles operation in the chain.
    
    Args:
        seconds: Delay in seconds between requests
    
    Example:
        >>> urls >> WithDelay(2.0) >> ExtractArticles()
    """
    
    def __init__(self, seconds: float, print_url: bool = False):
        if seconds < 0:
            raise ValueError("Delay must be non-negative")
        self.seconds = seconds
        self.print_url = print_url
    
    def _execute(self, data: Any) -> Any:
        """
        Execute delay setting (passes through data).
        
        Args:
            data: Pass-through data
            
        Returns:
            Same data (this is a configuration verb)
        """
        # This is primarily a marker for configuration
        # Actual delay handling is in ExtractArticles
        if self.print_url:
            logger.info(f"Setting delay to {self.seconds} seconds")
        return data


class Deduplicate(PipeBase):
    """
    Remove duplicate articles based on URL.
    
    This verb accepts a list of Articles or URLs and removes duplicates,
    keeping the first occurrence.
    
    Example:
        >>> articles >> Deduplicate()
    """
    
    def __init__(self, print_url: bool = False):
        self.print_url = print_url
    
    def _execute(self, data: Union[List[Any], pd.DataFrame, Any]) -> Any:
        """
        Execute deduplication.
        
        Args:
            data: List of articles/URLs or DataFrame
            
        Returns:
            Deduplicated data
        """
        if isinstance(data, list):
            seen = set()
            unique_items = []
            
            for item in data:
                # Handle both Article objects and raw strings (URLs)
                val = item.url if hasattr(item, 'url') else item
                if val not in seen:
                    seen.add(val)
                    unique_items.append(item)
            
            if self.print_url:
                logger.info(f"Deduplicated {len(data)} items to {len(unique_items)}")
            return unique_items
            
        if isinstance(data, pd.DataFrame) or is_pipeframe(data):
            # Default to deduplicating by URL if column exists
            is_pf = is_pipeframe(data)
            df = data._data if is_pf else data
            
            if 'url' in df.columns:
                unique_df = df.drop_duplicates(subset=['url'])
            else:
                unique_df = df.drop_duplicates()
                
            if self.print_url:
                logger.info(f"Deduplicated {len(df)} rows to {len(unique_df)}")
            return type(data)(unique_df) if is_pf else unique_df
            
        raise TypeError(f"Deduplicate expects list or DataFrame, got {type(data)}")


class Head(PipeBase):
    """
    Return the first N rows of a DataFrame.
    
    Args:
        n: Number of rows to return (default: 5)
    
    Example:
        >>> df >> Head(10)
    """
    
    def __init__(self, n: int = 5):
        if n < 1:
            raise ValueError("n must be at least 1")
        self.n = n
    
    def _execute(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Execute head operation.
        
        Args:
            data: DataFrame
            
        Returns:
            First n rows
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError(f"Head expects DataFrame, got {type(data)}")
        
        return data.head(self.n)


class SortBy(PipeBase):
    """
    Sort DataFrame by column(s).
    
    Args:
        by: Column name or list of column names
        ascending: Sort order (True for ascending, False for descending)
    
    Example:
        >>> df >> SortBy('date_published', ascending=False)
    """
    
    def __init__(self, by: Union[str, List[str]], ascending: bool = True):
        self.by = by
        self.ascending = ascending
    
    def _execute(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Execute sort operation.
        
        Args:
            data: DataFrame to sort
            
        Returns:
            Sorted DataFrame
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError(f"SortBy expects DataFrame, got {type(data)}")
        
        return data.sort_values(by=self.by, ascending=self.ascending)


