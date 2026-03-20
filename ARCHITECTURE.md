# pipescraper Architecture

This document explains the architecture, design decisions, and implementation details of pipescraper.

## 🏗️ Core Design Philosophy

pipescraper is built on three foundational principles:

1. **Natural Language Syntax** — Operations read like plain English
2. **Composability** — Small, focused verbs chain together
3. **Data Pipeline Thinking** — Data flows through transformations

### Inspiration

The pipe syntax is inspired by:
- **[pipeframe](https://github.com/Yasser03/pipeframe)** — Pandas with `>>` operator for dplyr-style chaining
- **[pipeplotly](https://github.com/Yasser03/pipeplotly)** — Grammar of Graphics visualization with pipes
- **Unix pipes** — Classic `|` operator philosophy
- **R's dplyr** — `%>%` magrittr pipe operator

## 📦 Package Structure

```
pipescraper/
├── pipescraper/
│   ├── __init__.py      # Package exports and API surface
│   ├── core.py          # Core data structures and extraction engines
│   ├── pipes.py         # Pipeable verb classes
│   └── utils.py         # Helper functions
├── tests/
│   └── test_pipescraper.py
├── examples/
│   └── basic_usage.py
└── [documentation files]
```

### Module Responsibilities

#### `core.py` — The Engine

Contains:
- **`Article`** dataclass — Immutable article representation
- **`LinkFetcher`** — Discovers article URLs from base pages
- **`ArticleExtractor`** — Extracts metadata using trafilatura + newspaper4k

**Why?** Separates extraction logic from user-facing API.

#### `pipes.py` — The Interface

Contains:
- **`PipeBase`** — Abstract base class for all pipe verbs
- **Pipe verbs** — `FetchLinks`, `ExtractArticles`, `ToDataFrame`, etc.

**Why?** Provides clean, composable API while encapsulating complexity.

#### `utils.py` — The Helpers

Contains:
- URL validation and normalization
- Text sanitization
- Domain extraction

**Why?** Keeps core modules focused; provides reusable utilities.

## 🔧 Implementation Details

### The Pipe Operator (`>>`)

All pipe verbs implement `__rrshift__` to enable the `>>` operator:

```python
class PipeBase:
    def __rrshift__(self, left):
        """Enable >> operator."""
        return self._execute(left)
    
    def _execute(self, data):
        """Subclasses implement this."""
        raise NotImplementedError
```

**How it works:**

1. Python evaluates `A >> B` as `B.__rrshift__(A)`
2. Our `__rrshift__` calls `_execute(A)`
3. `_execute` transforms the data and returns result
4. Result can be piped to next verb

**Example flow:**
```python
"url" >> FetchLinks() >> ExtractArticles()

# Evaluates as:
step1 = FetchLinks().__rrshift__("url")        # Returns list of URLs
step2 = ExtractArticles().__rrshift__(step1)   # Returns list of Articles
```

### Dual Extraction Engine

**Problem:** Trafilatura doesn't extract publication *time*, only *date*.

**Solution:** Use newspaper4k as supplementary parser.

```python
# Extract with trafilatura (primary)
metadata = trafilatura.extract_metadata(html)
text = trafilatura.extract(html)

# Supplement with newspaper4k for time
if extract_time:
    np_article = NewspaperArticle(url)
    np_article.download(input_html=html)
    np_article.parse()
    
    if np_article.publish_date:
        article.time_published = np_article.publish_date.strftime("%H:%M:%S")
```

### Google News URL Decoding (v0.3.0)

**Problem:** Google News URLs (e.g., `news.google.com/rss/articles/...`) often redirect to a consent wall ("Before you continue to Google"), which blocks headless extractors like trafilatura.

**Solution:** Mimetic `batchexecute` decoder.

PipeScraper implements a specialized `_decode_gnews_url` method that:
1.  Bypasses the consent wall using a specific `SOCS` (State of Consent) cookie.
2.  Mimics a browser's `batchexecute` request to resolve the encoded redirect.
3.  Performs this resolution in **parallel** using a `ThreadPoolExecutor` during discovery.

**Benefit:** Resolves 100% of Google News redirects into direct article URLs, enabling clean extraction.

**Trade-offs:**
- ✅ Get complete temporal metadata
- ✅ Keep trafilatura's superior text extraction
- ⚠️ Additional dependency (newspaper4k)
- ⚠️ Slightly slower (two parsing passes)

**Decision:** Worth it for complete metadata.

### Error Handling Strategy

Three-tier approach:

1. **Graceful Degradation** — Continue on individual failures
2. **Informative Logging** — Log warnings for debugging
3. **Optional Strict Mode** — `skip_errors=False` for strict pipelines

```python
def extract_batch(self, urls: List[str]) -> List[Article]:
    articles = []
    for url in urls:
        try:
            article = self.extract(url)
            if article:
                articles.append(article)
        except Exception as e:
            if self.skip_errors:
                logger.warning(f"Skipped {url}: {e}")
            else:
                raise
    return articles
```

### Type Safety

We use:
- **Dataclasses** for `Article` — Immutable, typed attributes
- **Type hints** throughout — Better IDE support and clarity
- **Runtime type checking** in pipes — Fail fast with helpful errors

```python
def _execute(self, data: List[Article]) -> pd.DataFrame:
    if not isinstance(data, list):
        raise TypeError(f"Expected list, got {type(data)}")
    # ...
```

## 🎯 Design Decisions

### Why Dataclasses for Article?

**Alternatives considered:**
- `dict` — Too flexible, no type safety
- `NamedTuple` — Immutable but no defaults
- Regular class — More boilerplate

**Chosen: Dataclasses**
- ✅ Immutable with frozen=False (flexibility for supplementation)
- ✅ Type hints built-in
- ✅ Clean `to_dict()` conversion
- ✅ Less boilerplate than regular classes

### Why Separate PipeBase Class?

**Could've:** Put `__rrshift__` in each verb class.

**Chose:** Base class for DRY and consistency.

Benefits:
- Single source of truth for pipe protocol
- Easy to add logging/profiling to all verbs
- Clear inheritance hierarchy
- Future extensibility (add hooks, validation)

### Why Both setup.py and pyproject.toml?

**Compatibility:**
- `pyproject.toml` — Modern standard (PEP 518, 621)
- `setup.py` — Backwards compatibility

Enables:
- Both `pip install .` and `python setup.py install`
- Support for older pip versions
- Easier migration for existing users

### Why Pandas DataFrame?

**Alternatives:**
- List of dicts — Less structured
- Custom class — Reinventing the wheel
- Polars — Newer, less adoption

**Chose: Pandas**
- ✅ Industry standard for data analysis
- ✅ Rich export options (CSV, JSON, Excel, Parquet)
- ✅ Familiar to target audience (data scientists)
- ✅ Easy filtering, sorting, grouping

## 🔄 Data Flow

### Complete Pipeline Flow

```
URL String
    ↓
FetchLinks (HTTP request + parsing)
    ↓
List[str] (article URLs)
    ↓
ExtractArticles (parallel extraction)
    ↓
List[Article] (structured metadata)
    ↓
FilterArticles (conditional filtering)
    ↓
List[Article] (filtered)
    ↓
ToDataFrame (conversion)
    ↓
pd.DataFrame
    ↓
SaveAs (export)
    ↓
pd.DataFrame (pass-through for chaining)
```

### Type Signatures

```python
str >> FetchLinks() → List[str]
List[str] >> ExtractArticles() → List[Article]
List[Article] >> FilterArticles(fn) → List[Article]
List[Article] >> ToDataFrame() → pd.DataFrame
pd.DataFrame >> SaveAs(path) → pd.DataFrame
```

## 🧪 Testing Strategy

### Three-Level Testing

1. **Unit Tests** — Individual functions and classes
2. **Integration Tests** — End-to-end pipelines
3. **Mock-Heavy** — Avoid real network requests

```python
@patch('requests.Session.get')
@patch('trafilatura.extract')
def test_extract(mock_extract, mock_get):
    # Mock HTTP and parsing
    mock_get.return_value = Mock(text="<html>...</html>")
    mock_extract.return_value = "Extracted text"
    
    # Test extraction
    article = extractor.extract("https://example.com")
    assert article.text == "Extracted text"
```

### Coverage Goals

- **Core modules** — >90% coverage
- **Pipe verbs** — >85% coverage
- **Utils** — 100% coverage (simple functions)

## 🚀 Performance Considerations

### Request Throttling

Built-in delays prevent:
- Rate limiting
- IP bans
- Server overload

Default: 1s between requests (configurable).

### Parallel Processing (v0.2.1 & v0.3.0)

PipeScraper uses `ThreadPoolExecutor` in two critical areas:
1.  **Article Extraction**: Parallelizing `ExtractArticles` across multiple URLs.
2.  **Google News Decoding**: Parallelizing the resolution of encoded URLs in `FetchGoogleNews`.

This combination reduces total pipeline time for 20 articles from ~45 seconds to ~10 seconds.

### Batch Processing

`extract_batch()` processes URLs sequentially with delays:

```python
def extract_batch(self, urls: List[str]) -> List[Article]:
    articles = []
    for url in urls:
        article = self.extract(url)  # Includes delay
        if article:
            articles.append(article)
    return articles
```

**Future optimization:** Async/await for parallelization while respecting delays.

### Memory Efficiency

- Stream URLs rather than loading all at once
- Optional `include_text=False` to exclude large text fields
- Generators possible for very large datasets (future)

## 🔮 Future Enhancements

### Planned Features

1. **Async Support** — `asyncio` for parallel extraction
2. **Progress Bars** — `tqdm` integration
3. **Caching** — Cache extracted articles
4. **More Filters** — Date ranges, keyword matching
5. **Custom Extractors** — Plugin system for custom parsers
6. **Streaming** — Generator-based processing for large datasets

### Extensibility Points

```python
# Custom extractor
class MyExtractor(ArticleExtractor):
    def extract(self, url: str) -> Optional[Article]:
        # Custom logic
        pass

# Custom pipe verb
class MyFilter(PipeBase):
    def _execute(self, data: List[Article]) -> List[Article]:
        # Custom filtering
        pass
```

## 📚 References

- **Trafilatura**: https://github.com/adbar/trafilatura
- **Newspaper4k**: https://github.com/AndyTheFactory/newspaper4k
- **PipeFrame**: https://github.com/Yasser03/pipeframe
- **PipePlotly**: https://github.com/Yasser03/pipeplotly

---

**Questions?** Open an issue on GitHub!

