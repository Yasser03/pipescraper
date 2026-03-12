# PipeScraper API Reference

Welcome to the PipeScraper API reference. This document provides detailed information about all public classes, functions, and pipeable verbs available in the `pipescraper` package.

---

## 🏗️ Core Classes

### `Article`
A dataclass representing a scraped news article.

**Attributes:**
- `url` (str): The article's URL.
- `source` (str): The domain/source.
- `title` (str): Article headline.
- `text` (str): Main article text content.
- `description` (str): Article description/summary.
- `author` (str): Article author(s).
- `date_published` (str): Publication date (YYYY-MM-DD).
- `time_published` (str): Publication time (HH:MM:SS).
- `language` (str): Detected language code.
- `tags` (List[str]): Article tags/categories.
- `image_url` (str): Main article image URL.
- `raw_metadata` (Dict): Additional metadata from the extraction engine.

**Methods:**
- `to_dict()`: Converts the article to a dictionary.

---

---

### `GoogleNewsFetcher`
Fetches news articles from Google News using high-performance parallel decoding.

**Constructor:**
`GoogleNewsFetcher(country='US', period='1d', max_results=10, print_url=False, search=None)`

**Attributes:**
- `search` (str or List[str]): Keywords or sentences to search for. If a list is provided, results are aggregated and deduplicated.
- `print_url` (bool): If True, prints URLs and status messages during execution.

**Methods:**
- `fetch_top_news()`: Main entry point. Handles discovery via `gnews` or `newspaper4k`, then performs parallel URL decoding to bypass consent walls.
- `_decode_gnews_url(url)`: Resolves encoded Google News URLs using a realistic `batchexecute` mimetic request.

### `ArticleExtractor`
Extracts structured metadata from article URLs.

**Constructor:**
`ArticleExtractor(timeout=10, delay=0.1, extract_time=False, user_agent='...')`

**Methods:**
- `extract(url)`: Extracts metadata for a single URL. Returns an `Article` or `None`.
- `extract_batch(urls, max_workers=None)`: Extracts metadata for multiple URLs in parallel using `ThreadPoolExecutor`.

---

## 🧪 Pipeable Verbs

Pipeable verbs are used with the `>>` operator to build scraping pipelines.

### `FetchLinks`
Fetch article links from a base URL.
- **Args:** `max_links` (int, optional), `respect_robots` (bool), `user_agent` (str), `timeout` (int), `delay` (float), `print_url` (bool).
- **Returns:** `List[str]` (article URLs).

### `FetchGoogleNews`
Fetch top news or search topics from Google News (new in v0.3.0).
- **Args:** `search` (str or list, optional), `country` (str), `period` (str), `max_results` (int), `print_url` (bool).
- **Returns:** `List[str]` (decoded article URLs).
- **Note:** Aggregates and deduplicates results when `search` is a list of queries.

### `ExtractArticles`
Extract article metadata from URLs.
- **Args:** `extract_time` (bool), `delay` (float), `timeout` (int), `skip_errors` (bool), `workers` (int, optional), `print_url` (bool).
- **Returns:** `List[Article]`.
- **Note:** Setting `workers` to 5-10 significantly speeds up batch extraction. Universal silence available via `print_url=False`.

### `ToDataFrame`
Convert articles to a pandas DataFrame.
- **Args:** `include_text` (bool).
- **Returns:** `pd.DataFrame`.

### `ToPipeFrame`
Convert articles to a PipeFrame DataFrame for dplyr-style manipulation.
- **Args:** `include_text` (bool).
- **Returns:** `PipeFrame`.

### `SaveAs`
Save data to a file.
- **Args:** `filepath` (str), `index` (bool).
- **Supported Formats:** `.csv`, `.json`, `.parquet`, `.xlsx`.

### `FilterArticles`
Filter list of Article objects.
- **Args:** `condition` (Callable[[Article], bool]).
- **Example:** `articles >> FilterArticles(lambda a: a.language == 'en')`

### `LimitArticles`
Limit the number of articles in the list.
- **Args:** `n` (int).

### `Deduplicate`
Remove duplicate articles based on URL.

### `WithDelay`
Set a delay (in seconds) for the next extraction step.

---

## 🔗 Integrations

### PipeFrame Verbs
When `pipeframe` is installed, the following verbs are available directly from `pipescraper`:
`select`, `filter_df`, `mutate`, `arrange`, `group_by`, `summarize`, `rename`, `distinct`, `pf_head`, `tail`, `slice_rows`.

### PipePlotly Verbs
When `pipeplotly` is installed, the following plotting verbs are available:
`ggplot`, `aes`, `geom_bar`, `geom_line`, `geom_point`, `geom_histogram`, `geom_box`, `labs`, `show`.

**Pre-built Charts:**
- `create_articles_by_source_chart()`
- `create_articles_timeline()`
- `create_text_length_distribution()`
- `create_articles_by_language()`

