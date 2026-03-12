"""
Core extraction logic and data structures for pipescraper.

This module contains the fundamental classes for article representation,
link fetching, and metadata extraction using trafilatura and newspaper4k.
"""

import json
import logging
import re
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from urllib.parse import urljoin, urlparse, quote
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup
import trafilatura
# Lazy import for newspaper to speed up loading and prevent top-level failures

from pipescraper.utils import is_valid_url, normalize_url, sanitize_text

logger = logging.getLogger(__name__)


@dataclass
class ScrapedArticle:
    """
    Represents a scraped news article with extracted metadata.
    
    Attributes:
        url: The article's URL
        source: The domain/source of the article
        title: Article headline
        text: Main article text content
        description: Article description/summary
        author: Article author(s)
        date_published: Publication date (YYYY-MM-DD)
        time_published: Publication time (HH:MM:SS) - extracted via newspaper4k
        language: Detected language code
        tags: Article tags/categories
        image_url: Main article image URL
        raw_metadata: Additional metadata from trafilatura
    """
    url: str
    source: str = ""
    title: str = ""
    text: str = ""
    description: str = ""
    author: str = ""
    date_published: str = ""
    time_published: str = ""
    language: str = ""
    tags: List[str] = field(default_factory=list)
    image_url: str = ""
    raw_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert article to dictionary representation."""
        return {
            'url': self.url,
            'source': self.source,
            'title': self.title,
            'text': self.text,
            'description': self.description,
            'author': self.author,
            'date_published': self.date_published,
            'time_published': self.time_published,
            'language': self.language,
            'tags': self.tags,
            'image_url': self.image_url,
        }

# Alias for backwards compatibility
Article = ScrapedArticle


class LinkFetcher:
    """
    Fetches and extracts article links from a given URL.
    
    This class crawls a base URL and identifies article links based on
    configurable patterns and heuristics.
    
    Attributes:
        respect_robots: Whether to respect robots.txt
        user_agent: User agent string for requests
        timeout: Request timeout in seconds
        delay: Delay between requests in seconds
    """
    
    def __init__(
        self,
        respect_robots: bool = True,
        user_agent: str = "pipescraper/0.1.0 (+https://github.com/pipescraper)",
        timeout: int = 10,
        delay: float = 0.1,
        print_url: bool = False,
    ):
        """
        Initialize the LinkFetcher.
        
        Args:
            respect_robots: Whether to check robots.txt
            user_agent: User agent for HTTP requests
            timeout: Request timeout in seconds
            delay: Delay between requests
        """
        self.respect_robots = respect_robots
        self.user_agent = user_agent
        self.timeout = timeout
        self.delay = delay
        self.print_url = print_url
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': user_agent})
        
    def can_fetch(self, url: str) -> bool:
        """
        Check if URL can be fetched according to robots.txt.
        
        Args:
            url: URL to check
            
        Returns:
            True if fetching is allowed, False otherwise
        """
        if not self.respect_robots:
            return True
            
        try:
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            rp = RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch(self.user_agent, url)
        except Exception as e:
            logger.warning(f"Error checking robots.txt for {url}: {e}")
            return True
    
    def fetch_links(self, base_url: str, max_links: Optional[int] = None) -> List[str]:
        """
        Fetch all article links from a base URL.
        
        Args:
            base_url: The base URL to scrape
            max_links: Maximum number of links to return (None for unlimited)
            
        Returns:
            List of article URLs found on the page
            
        Raises:
            ValueError: If URL is invalid
            requests.RequestException: If request fails
        """
        if not is_valid_url(base_url):
            raise ValueError(f"Invalid URL: {base_url}")
        
        if not self.can_fetch(base_url):
            if self.print_url:
                logger.warning(f"Robots.txt disallows fetching {base_url}")
            return []
        
        if self.print_url:
            logger.info(f"Fetching links from {base_url}")
        
        try:
            response = self._session.get(base_url, timeout=self.timeout)
            response.raise_for_status()
            time.sleep(self.delay)
        except requests.RequestException as e:
            if self.print_url:
                logger.error(f"Failed to fetch {base_url}: {e}")
            raise
        
        soup = BeautifulSoup(response.content, 'html.parser')
        links = set()
        
        # Extract all links from anchor tags
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            # Basic filtering for article-like URLs
            if self._is_article_link(absolute_url, base_url):
                links.add(normalize_url(absolute_url))
        
        link_list = list(links)
        
        if max_links:
            link_list = link_list[:max_links]
        
        if self.print_url:
            logger.info(f"Found {len(link_list)} article links")
        return link_list
    
    def _is_article_link(self, url: str, base_url: str) -> bool:
        """
        Heuristic to determine if a URL likely points to an article.
        
        Args:
            url: URL to check
            base_url: The base URL being scraped
            
        Returns:
            True if URL appears to be an article, False otherwise
        """
        parsed_base = urlparse(base_url)
        parsed_url = urlparse(url)
        
        # Must be same domain or subdomain
        if not (parsed_url.netloc == parsed_base.netloc or 
                parsed_url.netloc.endswith('.' + parsed_base.netloc)):
            return False
        
        # Exclude common non-article patterns
        exclude_patterns = [
            '/tag/', '/category/', '/author/', '/page/',
            '/all-about/', '/whats-on/', '/gallery/', '/video/',
            '/search', '/login', '/register', '/subscribe',
            '.pdf', '.jpg', '.png', '.gif', '.css', '.js',
            '#', 'mailto:', 'javascript:',
        ]
        
        url_lower = url.lower()
        if any(pattern in url_lower for pattern in exclude_patterns):
            return False
            
        # Path analysis
        path_parts = [p for p in parsed_url.path.split('/') if p]
        path_depth = len(path_parts)
        
        if path_depth == 0:
            return False

        # Strong Headline Signals
        import re
        last_part = path_parts[-1]
        
        # 1. Numeric ID indicator (common in news CMS)
        has_id = bool(re.search(r'-\d{6,15}$', last_part) or last_part.isdigit())
        
        # 2. Date indicator in URL
        has_date = bool(re.search(r'/\d{4}/\d{2}/\d{2}/', url_lower) or re.search(r'/\d{4}/\d{2}/', url_lower))
        
        # 3. "Long Slug" indicator (Headline-like rather than Category-like)
        # Most category hubs have short slugs (e.g., 'uk-news', 'health').
        # Most articles have long slugs (e.g., 'man-accused-of-murdering-ian-huntley-to-appear-in-court').
        slug_words = [w for w in last_part.split('-') if w]
        is_long_slug = len(slug_words) >= 4

        if has_id or has_date:
            return True
            
        # Refined Huber check: Hubs like /news/uk-news often have depth 2 and short slugs
        include_patterns = ['/article/', '/news/', '/story/', '/post/']
        is_news_area = any(pattern in url_lower for pattern in include_patterns)

        if is_news_area:
            # If it's a known news area, it's an article if it has a headline-like slug OR depth >= 3
            if is_long_slug:
                return True
            return path_depth >= 3
            
        # For non-news areas, require depth 3 AND a long slug or explicit article indicator
# For non-news areas, require depth 3 AND a long slug or explicit article indicator
        return path_depth >= 3 and is_long_slug


class GoogleNewsFetcher:
    """
    Fetches article links from Google News using newspaper4k.
    
    This class leverages newspaper4k's GoogleNewsSource to retrieve 
    top news or search-based news URLs.
    """
    
    def __init__(
        self,
        country: str = "US",
        period: str = "1d",
        max_results: int = 10,
        search: Optional[Union[str, List[str]]] = None,
        print_url: bool = False,
    ):
        """
        Initialize the GoogleNewsFetcher.
        
        Args:
            country: Country code (e.g., "US", "GB")
            period: Time period (e.g., "1h", "1d", "7d")
            max_results: Maximum number of results to fetch
            search: Keywords or sentences to search for
            print_url: Whether to show detailed output
        """
        self.country = country
        self.period = period
        self.max_results = max_results
        self.search = search
        self.print_url = print_url
        
        # URL encoding related constants (ported from newspaper4k)
        self._ENCODED_URL_PREFIX = "https://news.google.com/rss/articles/"
        self._ENCODED_URL_RE = re.compile(rf"^{re.escape(self._ENCODED_URL_PREFIX)}(?P<encoded_url>[^?]+)")

    def _decode_gnews_url(self, url: str) -> Optional[str]:
        """
        Internal helper to decode a Google News redirect URL.
        Ported from newspaper4k's batchexecute implementation.
        """
        if not url.startswith(self._ENCODED_URL_PREFIX):
            return url

        try:
            match = self._ENCODED_URL_RE.match(url)
            if not match:
                return url
                
            data_id = match.groupdict()["encoded_url"]
            
            # Use requests to get the page with specific data-n-a-id
            # Add SOCS cookie to bypass Google consent wall
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://news.google.com/'
            }
            cookies = {
                'SOCS': 'CAESEwgDEgk0ODE3Nzk3OTQaAmVuIAEaBgiA_LyaBg'
            }
            response = requests.get(url, headers=headers, cookies=cookies, timeout=10)
            if response.status_code != 200:
                return url

            soup = BeautifulSoup(response.content, 'html.parser')
            data_node = soup.find('div', attrs={"data-n-a-id": data_id})
            
            if not data_node:
                return url
                
            signature = data_node.get("data-n-a-sg")
            timestamp = data_node.get("data-n-a-ts")
            
            if signature and timestamp:
                google_url = "https://news.google.com/_/DotsSplashUi/data/batchexecute"
                payload = [
                    "Fbv4je",
                    f'["garturlreq",[["X","X",["X","X"],null,null,1,1,"US:en",null,1,null,null,null,null,null,0,1],"X","X",1,[1,1,1],1,1,null,0,0,null,0],"{data_id}",{timestamp},"{signature}"]',
                ]
                req_data = f"f.req={quote(json.dumps([[payload]]))}"
                
                headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'
                post_res = requests.post(google_url, data=req_data, headers=headers, timeout=10)
                
                if post_res.status_code == 200:
                    # Parse the batchexecute response
                    parts = post_res.text.split("\n", 1)[-1]
                    try:
                        res_json = json.loads(parts)
                        inner_data = json.loads(res_json[0][2])
                        decoded = inner_data[1]
                        if self.print_url:
                            logger.info(f"Decoded {url} -> {decoded}")
                        return decoded
                    except (json.JSONDecodeError, IndexError, TypeError) as e:
                        logger.debug(f"JSON parse error for {url}: {e}")
                else:
                    logger.debug(f"Post failed for {url}: status {post_res.status_code}")
            else:
                logger.debug(f"Missing signature/timestamp for {url}: sig={signature}, ts={timestamp}")
                        
            return url
        except Exception as e:
            logger.debug(f"Failed to decode Google News URL {url}: {e}")
            return url
        
    def fetch_top_news(self) -> List[str]:
        """
        Fetch news article URLs from Google News (top news or search).
        
        Returns:
            List of unique article URLs
        """
        # Method 1: Try newspaper4k's integrated Google News source
        original_levels = {}
        if not self.print_url:
            # Suppress noisy external loggers
            external_loggers = [
                'newspaper', 'gnews', 'urllib3', 'requests', 
                'newspaper.google_news', 'gnews.gnews'
            ]
            for logger_name in external_loggers:
                ext_logger = logging.getLogger(logger_name)
                original_levels[logger_name] = ext_logger.level
                ext_logger.setLevel(logging.WARNING)
        
        try:
            # Method 1: Try direct gnews package (Faster)
            try:
                from gnews import GNews
                google_news = GNews(language='en', country=self.country, period=self.period, max_results=self.max_results)
                
                all_urls = []
                if self.search:
                    search_queries = [self.search] if isinstance(self.search, str) else self.search
                    for query in search_queries:
                        if self.print_url:
                            logger.info(f"Searching Google News for: '{query}' ({self.country}, {self.period})")
                        news_items = google_news.get_news(query)
                        all_urls.extend([item['url'] for item in news_items if 'url' in item])
                else:
                    if self.print_url:
                        logger.info(f"Fetching top news from Google News using gnews ({self.country}, {self.period})")
                    news_items = google_news.get_top_news()
                    all_urls.extend([item['url'] for item in news_items if 'url' in item])
                
                # Deduplicate while preserving order
                urls = list(dict.fromkeys(all_urls))[:self.max_results]
                
                if urls:
                    if self.print_url:
                        logger.info(f"Found {len(urls)} articles from Google News using direct gnews package. Decoding URLs...")
                    
                    # Parallel decoding for gnews URLs to avoid consent wall
                    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
                        decoded_urls = list(executor.map(self._decode_gnews_url, urls))
                    
                    # Filter out None and return decoded URLs
                    final_urls = [u for u in decoded_urls if u]
                    if self.print_url:
                        logger.info(f"Successfully decoded {len(final_urls)} Google News URLs")
                    return final_urls
            except ImportError:
                logger.debug("gnews package not installed. Trying newspaper4k fallback...")
            except Exception as e:
                logger.debug(f"Direct gnews execution failed: {e}. Trying newspaper4k fallback...")

            # Method 2: Try newspaper4k's integrated Google News source (Slower, decodes URLs)
            try:
                from newspaper.google_news import GoogleNewsSource
                if self.print_url:
                    logger.info(f"Fetching top news from Google News using newspaper4k ({self.country}, {self.period})")
                
                source = GoogleNewsSource(
                    country=self.country,
                    period=self.period,
                    max_results=self.max_results
                )
                source.build(top_news=True)
                urls = source.article_urls()
                
                if urls:
                    if self.print_url:
                        logger.info(f"Found {len(urls)} articles from Google News using newspaper4k")
                    return urls
                else:
                    logger.debug("Google News (newspaper4k) returned 0 articles. Trying default build...")
                    source.build() # Try default build
                    urls = source.article_urls()
                    if urls:
                        if self.print_url:
                            logger.info(f"Found {len(urls)} articles using newspaper4k default build")
                        return urls
            except ImportError as e:
                logger.debug(f"newspaper.google_news import failed: {e}.")
            except Exception as e:
                logger.debug(f"GoogleNewsSource execution failed: {e}.")

            # If both fail or return nothing
            if not urls:
                if self.print_url:
                    logger.error(
                        "Failed to fetch Google News articles. This may be due to missing dependencies.\n"
                        "Please run: pip install 'newspaper4k[gnews] gnews'\n"
                        "If you are in a Jupyter notebook, also run: !pip install 'newspaper4k[gnews] gnews'"
                    )
            
            return urls
            
        finally:
            if not self.print_url:
                # Restore original log levels
                for logger_name, level in original_levels.items():
                    logging.getLogger(logger_name).setLevel(level)


class ArticleExtractor:
    """
    Extracts structured metadata from article URLs using trafilatura and newspaper4k.
    
    This class handles the extraction of article content and metadata, with
    trafilatura as the primary engine and newspaper4k supplementing time-of-publish
    data which trafilatura does not provide.
    
    Design Decision:
        Trafilatura excels at content extraction but only provides publication dates,
        not times. To capture full temporal metadata, we use newspaper4k as a
        supplementary parser specifically for extracting publish_date with time
        component. This dual-engine approach maximizes metadata completeness.
    
    Attributes:
        timeout: Request timeout in seconds
        delay: Delay between requests
        extract_time: Whether to extract publication time and date using newspaper4k
    """
    
    def __init__(
        self,
        timeout: int = 10,
        delay: float = 0.1,
        extract_time: bool = True,
        user_agent: str = "pipescraper/0.1.0 (+https://github.com/pipescraper)",
        print_url: bool = False,
    ):
        """
        Initialize the ArticleExtractor.
        
        Args:
            timeout: Request timeout in seconds
            delay: Delay between article extractions
            extract_time: Whether to extract date and time using newspaper4k (default: True)
            user_agent: User agent for requests
            print_url: Whether to show detailed output
        """
        self.timeout = timeout
        self.delay = delay
        self.extract_time = extract_time
        self.user_agent = user_agent
        self.print_url = print_url
        self._session = requests.Session()
        self._session.headers.update({'User-Agent': user_agent})
    
    def extract(self, url: str) -> Optional[ScrapedArticle]:
        """
        Extract article metadata from a URL.
        
        Args:
            url: Article URL to extract
            
        Returns:
            Article object with extracted metadata, or None if extraction fails
        """
        original_levels = {}
        if not self.print_url:
            # Suppress noisy external loggers
            external_loggers = ['newspaper', 'trafilatura', 'urllib3', 'requests']
            for logger_name in external_loggers:
                ext_logger = logging.getLogger(logger_name)
                original_levels[logger_name] = ext_logger.level
                ext_logger.setLevel(logging.WARNING)
        
        try:
            if self.print_url:
                logger.info(f"Extracting article from {url}")
            
            try:
                # Fetch the page content
                response = self._session.get(url, timeout=self.timeout)
                response.raise_for_status()
                html_content = response.text
                time.sleep(self.delay)
            except requests.RequestException as e:
                if self.print_url:
                    logger.error(f"Failed to fetch {url}: {e}")
                return None
            
            # Extract using trafilatura (primary engine)
            # Use return_fallback=True to get more metadata if primary extraction fails
            metadata = trafilatura.extract_metadata(html_content)
            extracted_text = trafilatura.extract(html_content, include_comments=False)
            
            if not extracted_text and not metadata:
                if self.print_url:
                    logger.warning(f"No content extracted from {url}")
                return None
            
            # Determine canonical URL and source using Trafilatura metadata
            # Trafilatura's sitename is much cleaner than a raw netloc
            canonical_url = metadata.url if metadata and metadata.url else url
            source_fallback = urlparse(url).netloc
            source = metadata.sitename if metadata and metadata.sitename else (
                metadata.hostname if metadata and metadata.hostname else source_fallback
            )
            
            # Build article from trafilatura data
            article = ScrapedArticle(
                url=canonical_url,
                source=source,
                title=metadata.title if metadata and metadata.title else "",
                text=sanitize_text(extracted_text) if extracted_text else "",
                description=metadata.description if metadata and metadata.description else "",
                author=metadata.author if metadata and metadata.author else "",
                date_published=metadata.date if metadata and metadata.date else "",
                language=metadata.language if metadata and metadata.language else "",
                tags=metadata.tags if metadata and metadata.tags else [],
                image_url=metadata.image if metadata and metadata.image else "",
            )
            
            # Supplement with newspaper4k ONLY if requested and if time is missing
            if self.extract_time and not article.time_published:
                np_article = None
                try:
                    # Lazy import inside the method
                    import newspaper
                    if hasattr(newspaper, 'Article'):
                        NewspaperArticleClass = newspaper.Article
                        
                        # Ensure it's not our own class (shadowing check)
                        if NewspaperArticleClass is not ScrapedArticle:
                            # Ensure we use download(input_html=...) as required by newspaper4k
                            np_article = NewspaperArticleClass(url)
                            np_article.download(input_html=html_content)
                            np_article.parse()
                            
                            # Extract publication date and time if available
                            if getattr(np_article, 'publish_date', None):
                                pub_datetime = np_article.publish_date
                                
                                if not article.date_published:
                                    article.date_published = pub_datetime.strftime("%Y-%m-%d")
                                
                                article.time_published = pub_datetime.strftime("%H:%M:%S")
                                logger.debug(f"Extracted date: {article.date_published}, time: {article.time_published}")
                except (ImportError, Exception) as e:
                    logger.warning(f"Optional newspaper4k extraction failed for {url}: {e}")
            
            # Store raw metadata for advanced users
            if metadata:
                article.raw_metadata = {
                    'sitename': metadata.sitename,
                    'hostname': metadata.hostname,
                    'categories': metadata.categories,
                    'pagetype': metadata.pagetype,
                }
            
            if self.print_url:
                logger.info(f"Successfully extracted: {article.title[:50]}...")
            return article
            
        finally:
            if not self.print_url:
                # Restore original log levels
                for logger_name, level in original_levels.items():
                    logging.getLogger(logger_name).setLevel(level)
    
    def extract_batch(self, urls: List[str], max_workers: Optional[int] = None) -> List[ScrapedArticle]:
        """
        Extract article metadata from a list of URLs in parallel.
        
        Args:
            urls: List of article URLs
            max_workers: Maximum number of parallel workers (None for default)
            
        Returns:
            List of ScrapedArticle objects
        """
        if not urls:
            return []
            
        if self.print_url:
            logger.info(f"Extracting batch of {len(urls)} articles (max_workers={max_workers})")
        
        articles = []
        
        # Use ThreadPoolExecutor for parallel extraction
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Map the extract method to all URLs
            results = list(executor.map(self.extract, urls))
            
            # Filter out None results (failed extractions)
            articles = [a for a in results if a is not None]
        
        if self.print_url:
            logger.info(f"Extracted {len(articles)} of {len(urls)} articles")
        return articles
