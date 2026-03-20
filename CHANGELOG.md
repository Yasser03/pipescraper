# Changelog

All notable changes to pipescraper will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-03-12

### Added
- **Google News Search** — Added `search` parameter to `FetchGoogleNews` and `GoogleNewsFetcher`. Supports single keywords, lists of queries, or full sentences.
- **Smart Query Aggregation** — Automatically merges and deduplicates results when multiple search terms are provided.
- **High-Performance URL Decoding** — Implemented a parallel `batchexecute` decoder that bypasses Google's consent wall ("Before you continue").
- **Universal Pipeline Silence** — All pipes now support `print_url=False` (default), ensuring absolute pipeline silence unless explicitly requested.

### Changed
- **Google News Discovery** — Now prioritizes the `gnews` package for discovery, with a fallback to `newspaper4k`.
- **Parallel Decoding** — Decoding happens in parallel using `ThreadPoolExecutor`, reducing total fetch-to-extract time by ~75%.
- **Robustness** — Added specific consent-bypassing cookies and headers to decoding requests.

## [0.2.3] - 2026-03-07

### Fixed
- **Newspaper4k Attribute Error** — Resolved `AttributeError: 'Article' object has no attribute 'set_html'` by renaming internal `Article` class to `ScrapedArticle` to avoid name collisions with `newspaper.Article`.
- **Robust Extraction** — Improved stability when extracting publication time; the library now gracefully handles missing or broken `newspaper` installations.

## [0.2.2] - 2026-03-07

### Fixed
- **PipeFrame Import Error** — Resolved `ImportError` on systems where certain PipeFrame verbs (like `sample`) are missing or have different export locations.
- **Robust Integration** — Implemented defensive attribute access for all conditional integration verbs.

## [0.2.1] - 2026-03-07

### Added
- **Parallel Scraping** — Significantly faster batch article extraction using `ThreadPoolExecutor`.
- **`workers` parameter** — Added to `ExtractArticles` pipe verb for parallel execution.
- **`max_workers` parameter** — Added to `ArticleExtractor.extract_batch` method.
- **Enhanced Documentation** — Updated Tutorial, Quickstart, and README with parallel scraping examples.

### Changed
- **Performance Optimization** — Achieved ~73% reduction in scraping time for batches.
- **ArticleExtractor.extract_batch** — Now uses parallel processing by default if workers are specified.

## [0.2.0] - 2024-01-20

### Added
- **PipeFrame integration** — Seamless integration with PipeFrame for data manipulation
- **ToPipeFrame verb** — Convert articles directly to PipeFrame DataFrames
- **PipePlotly integration** — Complete Grammar of Graphics visualization support
- **All PipeFrame verbs** — Direct access to select, filter, mutate, arrange, group_by, summarize, etc.
- **All PipePlotly functions** — Direct access to ggplot, aes, geom_*, labs, theme_*, etc.
- **Helper visualizations** — Pre-built functions for common article visualizations:
  - `create_articles_by_source_chart()`
  - `create_articles_timeline()`
  - `create_text_length_distribution()`
  - `create_articles_by_language()`
- **Optional dependencies** — Install extras with `[pipeframe]`, `[pipeplotly]`, or `[all]`
- **Advanced examples** — New `examples/advanced_integration.py` with 8 integration examples
- **Integration modules** — `pipeframe_integration.py` and `pipeplotly_integration.py`

### Changed
- **Version bump** — 0.1.0 → 0.2.0
- **Enhanced README** — Added PipeFrame and PipePlotly sections with examples
- **Updated requirements** — Optional dependencies clearly documented
- **setup.py and pyproject.toml** — Added optional dependency groups

### Features
- **Complete end-to-end pipelines** — Scrape → Transform → Visualize → Save
- **Zero API changes** — Fully backward compatible with 0.1.0
- **Graceful degradation** — PipeFrame/PipePlotly features available only when installed
- **Availability checks** — `PIPEFRAME_AVAILABLE` and `PIPEPLOTLY_AVAILABLE` flags

## [0.1.0] - 2024-01-15

### Added
- Initial release of pipescraper
- Core pipe-based syntax using `>>` operator
- `FetchLinks` verb for discovering article URLs from news sites
- `ExtractArticles` verb for metadata extraction via trafilatura and newspaper4k
- `ToDataFrame` verb for converting to pandas DataFrame
- `SaveAs` verb supporting CSV, JSON, Excel, and Parquet formats
- `FilterArticles` verb for conditional filtering
- `LimitArticles` verb for limiting result sets
- `Deduplicate` verb for removing duplicate articles by URL
- `Article` dataclass with comprehensive metadata fields
- Publication time extraction via newspaper4k (supplements trafilatura's date-only extraction)
- Robots.txt compliance and request throttling
- Comprehensive test suite with pytest
- Full documentation and usage examples
- Type hints throughout codebase
- Google-style docstrings

### Features
- **11 metadata fields extracted**: url, source, title, text, description, author, date_published, time_published, language, tags, image_url
- **Dual extraction engine**: trafilatura (primary) + newspaper4k (time supplementation)
- **Multiple export formats**: CSV, JSON, Excel (.xlsx), Parquet
- **Respectful scraping**: Built-in delays, robots.txt checking, user-agent configuration
- **Error handling**: Graceful degradation with skip_errors option
- **Pandas integration**: Direct DataFrame output for analysis

### Design Decisions
- Chose dual-engine approach (trafilatura + newspaper4k) to capture both high-quality content extraction and full timestamp metadata
- Implemented pipe syntax via `__rrshift__` following pipeframe/pipeplotly patterns
- Used dataclasses for Article representation for immutability and type safety
- Made all pipe verbs inherit from PipeBase for consistent interface

[0.2.3]: https://github.com/Yasser03/pipescraper/releases/tag/v0.2.3
[0.2.2]: https://github.com/Yasser03/pipescraper/releases/tag/v0.2.2
[0.2.1]: https://github.com/Yasser03/pipescraper/releases/tag/v0.2.1
[0.2.0]: https://github.com/Yasser03/pipescraper/releases/tag/v0.2.0
[0.1.0]: https://github.com/Yasser03/pipescraper/releases/tag/v0.1.0

