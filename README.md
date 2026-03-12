# pipescraper 🔗

**A pipe-based news article scraping and metadata extraction library for Python**

pipescraper provides a natural language verb-based interface for scraping news websites and extracting structured article metadata using the intuitive pipe (`>>`) operator. Built on top of [trafilatura](https://github.com/adbar/trafilatura) with supplementary time extraction via [newspaper3k](https://github.com/codelucas/newspaper/), pipescraper combines powerful extraction capabilities with an elegant, chainable API.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## ✨ Features

- **🔗 Pipe-based syntax** — Chain operations naturally with the `>>` operator
- **📰 Comprehensive metadata extraction** — Extract URL, source, title, text, author, dates, language, and more
- **⏰ Publication time parsing** — Supplement trafilatura's date extraction with full timestamp support
- **🤖 Respectful scraping** — Built-in robots.txt compliance and request throttling
- **� Google News Search** — Search for keywords or sentences across regions and time periods ⭐ NEW
- **🧠 Automatic URL Decoding** — Parallel `batchexecute` decoder for Google News (bypasses consent wall) ⭐ NEW
- **�📊 Pandas integration** — Export to DataFrame with CSV, JSON, Excel support
- **🎯 Flexible filtering** — Filter articles by language, author, content length, or custom criteria
- **🧹 Automatic deduplication** — Remove duplicate articles by URL
- ⚡ **Parallel Scraping** — Turbocharge batch extraction with multi-threaded workers
- **🚀 Production-ready** — Comprehensive error handling and logging
- **🔧 PipeFrame integration** — Use all PipeFrame verbs (select, filter, mutate, arrange, etc.) for data manipulation
- **📈 PipePlotly integration** — Create visualizations with Grammar of Graphics using ggplot, geom_bar, geom_point, etc.

## 🎨 Optional Integrations

### PipeFrame - Data Manipulation

Install PipeFrame for advanced data manipulation with dplyr-style verbs:

```bash
pip install pipescraper[pipeframe]
# or
pip install pipeframe
```

Use all PipeFrame verbs directly in your pipelines:

```python
from pipescraper import FetchLinks, ExtractArticles, ToPipeFrame
from pipeframe import select, filter, mutate, arrange, group_by, summarize

result = ("https://news-site.com" >> 
          FetchLinks(max_links=20) >>
          ExtractArticles() >>
          ToPipeFrame() >>
          select('title', 'author', 'date_published', 'text') >>
          mutate(text_length=lambda df: df['text'].str.len()) >>
          filter(lambda df: df['author'].notna()) >>
          arrange('date_published', ascending=False) >>
          group_by('author') >>
          summarize(article_count=('title', 'count')))
```

### PipePlotly - Visualization

Install PipePlotly for Grammar of Graphics visualizations:

```bash
pip install pipescraper[pipeplotly]
# or
pip install pipeplotly
```

Create visualizations directly from your pipelines:

```python
from pipescraper import FetchLinks, ExtractArticles, ToPipeFrame
from pipeframe import mutate
from pipeplotly import ggplot, aes, geom_bar, geom_point, labs, theme_minimal

# Bar chart of articles by source
fig = ("https://news-site.com" >> 
       FetchLinks(max_links=20) >>
       ExtractArticles() >>
       ToPipeFrame() >>
       ggplot(aes(x='source')) >>
       geom_bar() >>
       labs(title='Articles by Source', x='Source', y='Count') >>
       theme_minimal())

fig.show()

# Scatter plot with text length
fig = ("https://news-site.com" >> 
       FetchLinks(max_links=20) >>
       ExtractArticles() >>
       ToPipeFrame() >>
       mutate(text_length=lambda df: df['text'].str.len()) >>
       ggplot(aes(x='date_published', y='text_length', color='source')) >>
       geom_point() >>
       labs(title='Article Length Over Time', x='Date', y='Length'))

fig.show()
```

### Install Everything

```bash
pip install pipescraper[all]
```

## 🚀 Quick Start

### Installation

```bash
pip install pipescraper
```

Or install from source:

```bash
git clone https://github.com/Yasser03/pipescraper.git
cd pipescraper
pip install -e .
```

### Basic Usage

```python
from pipescraper import FetchLinks, ExtractArticles, ToDataFrame, SaveAs

# Simple pipeline: URL → Links → Articles → DataFrame → CSV
("https://news-site.com" >> 
 FetchLinks(max_links=10) >> 
 ExtractArticles() >> 
 ToDataFrame() >> 
 SaveAs("articles.csv"))
```

That's it! You've just scraped 10 articles and saved them to CSV. 🎉

## 📖 Documentation

### Core Pipe Verbs

pipescraper provides a set of composable "verb" operations that can be chained using `>>`:

#### `FetchLinks()`
Fetch article links from a base URL.

```python
links = "https://news-site.com" >> FetchLinks(
    max_links=50,           # Maximum number of links to fetch
    respect_robots=True,    # Respect robots.txt
    delay=1.0,             # Delay between requests (seconds)
    timeout=10,            # Request timeout (seconds)
)
```

#### `ExtractArticles()`
Extract metadata from article URLs.

```python
articles = urls >> ExtractArticles(
    workers=5,              # Number of parallel workers
    delay=0.1,              # Delay between extractions
    extract_time=True,      # Extract publication time via newspaper4k
    skip_errors=True,       # Skip failed extractions
    timeout=10,             # Request timeout
    print_url=False,        # Silence individual URL logging (new in v0.3.0)
)
```

#### `FetchGoogleNews()`
Fetch top news or search for specific topics from Google News (new in v0.3.0).

```python
# Fetch top news from a specific country
articles = FetchGoogleNews(
    country="US",           # ISO country code (US, UK, CA, FR, etc.)
    period="1d",            # Time period (1h, 1d, 7d, 1y)
    max_results=10,         # Limit results
    print_url=False,        # Absolute pipeline silence
)

# Search for keywords or sentences
search_articles = FetchGoogleNews(
    search="SpaceX Mars mission", # String search
    # OR search=["Iran", "USA war"] # List of queries
    max_results=10,
)
```
> [!NOTE]
> PipeScraper uses a high-performance parallel decoder to resolve Google News URLs, bypassing the "Before you continue to Google" consent wall automatically.

#### `ToDataFrame()`
Convert articles to pandas DataFrame.

```python
df = articles >> ToDataFrame(
    include_text=True       # Include full article text (can be large)
)
```

#### `ToPipeFrame()`
Convert articles to PipeFrame DataFrame (requires pipeframe).

```python
pf = articles >> ToPipeFrame(
    include_text=True       # Include full article text (can be large)
)

# Now use PipeFrame verbs
from pipeframe import select, filter, arrange

result = (pf >>
          select('title', 'author', 'date_published') >>
          filter(lambda df: df['author'].notna()) >>
          arrange('date_published', ascending=False))
```

#### `SaveAs()`
Save DataFrame to file (CSV, JSON, Excel, Parquet).

```python
# Auto-detects format from extension
df >> SaveAs("output.csv")
df >> SaveAs("output.json")
df >> SaveAs("output.xlsx")
df >> SaveAs("output.parquet")
```

#### `FilterArticles()`
Filter articles by custom criteria.

```python
# Filter by author presence
articles >> FilterArticles(lambda a: bool(a.author))

# Filter by language
articles >> FilterArticles(lambda a: a.language == 'en')

# Filter by text length
articles >> FilterArticles(lambda a: len(a.text) > 1000)
```

#### `LimitArticles()`
Limit number of articles.

```python
articles >> LimitArticles(10)  # Keep first 10
```

#### `Deduplicate()`
Remove duplicate articles by URL.

```python
articles >> Deduplicate()
```

### Complete Examples

#### Example 1: Filtered Pipeline

```python
from pipescraper import *

# Scrape English articles with authors, limit to 20, save as Excel
result = ("https://news-site.com" >> 
          FetchLinks(max_links=50) >>
          ExtractArticles(delay=2.0) >>
          FilterArticles(lambda a: a.language == 'en') >>
          FilterArticles(lambda a: bool(a.author)) >>
          LimitArticles(20) >>
          Deduplicate() >>
          ToDataFrame(include_text=False) >>
          SaveAs("filtered_articles.xlsx"))

print(f"Saved {len(result)} articles")
```

#### Example 2: Direct Article Extraction

```python
# Extract from a specific URL without fetching links
article_url = "https://news-site.com/specific-article"

df = (article_url >>
      ExtractArticles() >>
      ToDataFrame() >>
      SaveAs("single_article.json"))
```

#### Example 3: Turbo Parallel Pipeline (v0.2.1+)

```python
from pipescraper import *

# Scrape 50 articles in parallel using 10 workers
df = ("https://news-site.com" >> 
      FetchLinks(max_links=50) >>
      ExtractArticles(workers=10) >>
      ToDataFrame())

print(f"Scraped {len(df)} articles in record time!")
```

#### Example 4: Mixed Topic Search (v0.3.0+)

```python
from pipescraper import *

# Search for multiple related topics; results are aggregated and deduplicated
search_articles = (FetchGoogleNews(
                        search=["latest AI breakthroughs", "quantum computing news"],
                        period="7d",
                        max_results=20) >> 
                   ExtractArticles(workers=5) >> 
                   ToDataFrame())

print(f"Found {len(search_articles)} unique articles across all search terms!")
```

#### Example 4: Inspect Before Saving

#### Example 4: Respectful Scraping

```python
# Configure delays and robots.txt compliance
result = ("https://news-site.com" >> 
          FetchLinks(
              max_links=10,
              respect_robots=True,  # Check robots.txt
              delay=3.0,            # 3s delay between page requests
              user_agent="MyBot/1.0 (contact@example.com)"
          ) >>
          ExtractArticles(delay=3.0) >>  # 3s delay between articles
          ToDataFrame() >>
          SaveAs("respectful_scrape.csv"))
```

### Extracted Metadata Fields

Each article contains the following fields:

| Field            | Description                   | Source                    |
| ---------------- | ----------------------------- | ------------------------- |
| `url`            | Article URL                   | Input                     |
| `source`         | Domain/source name            | Parsed                    |
| `title`          | Article headline              | Trafilatura / newspaper3k |
| `text`           | Main article content          | Trafilatura               |
| `description`    | Article summary               | Trafilatura               |
| `author`         | Author name(s)                | Trafilatura / newspaper3k |
| `date_published` | Publication date (YYYY-MM-DD) | Trafilatura / newspaper3k |
| `time_published` | Publication time (HH:MM:SS)   | **newspaper3k** ⭐         |
| `language`       | Language code (e.g., 'en')    | Trafilatura               |
| `tags`           | Article tags/categories       | Trafilatura               |
| `image_url`      | Main article image            | Trafilatura / newspaper3k |

⭐ **Note**: `time_published` is extracted via newspaper3k to supplement trafilatura, which only provides dates.

## 🆚 Feature Comparison

### pipescraper vs. Trafilatura

| Feature               | pipescraper         | Trafilatura   |
| --------------------- | ------------------- | ------------- |
| Content extraction    | ✅ (via trafilatura) | ✅             |
| Metadata extraction   | ✅ Enhanced          | ✅ Basic       |
| Publication time      | ✅ (via newspaper3k) | ❌ (date only) |
| Pipe syntax           | ✅                   | ❌             |
| Link discovery        | ✅                   | ❌             |
| Batch processing      | ✅                   | Manual        |
| DataFrame export      | ✅ (CSV/JSON/Excel)  | ❌             |
| Filtering             | ✅ Built-in          | Manual        |
| Robots.txt compliance | ✅                   | Manual        |
| Request throttling    | ✅ Configurable      | Manual        |

### Why pipescraper?

**Trafilatura** excels at extracting clean text from HTML, but it:
- Only provides publication **dates**, not times
- Doesn't include link discovery or batch scraping workflows
- Requires manual orchestration for end-to-end pipelines

**pipescraper** builds on trafilatura's strengths and adds:
- ⏰ **Full timestamp extraction** via newspaper3k supplementation
- 🔗 **Pipe-based syntax** for readable, chainable workflows
- 🤖 **Built-in scraping infrastructure** (link discovery, throttling, robots.txt)
- 📊 **Pandas integration** for immediate data analysis and export
- 🎯 **Declarative filtering** without manual loops

### Design Decision: Dual Extraction Engine

pipescraper uses a **dual-engine approach**:

1. **Trafilatura** (primary) — Industry-leading content extraction with excellent precision
2. **newspaper3k** (supplementary) — Specifically for `time_published` field extraction

**Why?** Trafilatura's `extract_metadata()` returns only dates (`2024-01-15`), not times. To capture full temporal metadata (`14:30:00`), we supplement with newspaper3k's `publish_date` parser. This maximizes metadata completeness while maintaining trafilatura's superior text extraction quality.

## 🛠️ Development

### Setup

```bash
# Clone repository
git clone https://github.com/Yasser03/pipescraper.git
cd pipescraper

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=pipescraper --cov-report=html

# Run specific test file
pytest tests/test_pipescraper.py -v
```

### Project Structure

```
pipescraper/
├── pipescraper/
│   ├── __init__.py      # Package exports
│   ├── core.py          # Article, LinkFetcher, ArticleExtractor
│   ├── pipes.py         # Pipe verb classes (FetchLinks, etc.)
│   └── utils.py         # Helper functions
├── tests/
│   └── test_pipescraper.py  # Test suite
├── examples/
│   └── basic_usage.py   # Usage examples
├── README.md
├── setup.py
├── requirements.txt
└── LICENSE
```

## 📋 Requirements

- Python 3.8+
- trafilatura >= 1.6.0
- newspaper3k >= 0.2.8
- pandas >= 1.3.0
- requests >= 2.27.0
- beautifulsoup4 >= 4.10.0

See `requirements.txt` for full dependencies.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## �‍💻 Author

**Dr. Yasser Mustafa**

*AI & Data Science Specialist | Theoretical Physics PhD*

- 🎓 PhD in Theoretical Nuclear Physics
- 💼 10+ years in production AI/ML systems
- 🔬 48+ research publications
- 🏢 Experience: Government (Abu Dhabi), Media (Track24), Recruitment (Reed), Energy (ADNOC)
- 📍 Based in Newcastle Upon Tyne, UK
- ✉️ yasser.mustafan@gmail.com
- 🔗 [LinkedIn](https://www.linkedin.com/in/yasser-mustafa-phd-72886344/) | [GitHub](https://github.com/Yasser03)

**PipeScraper** was born from the need for a more intuitive, pipe-based approach to news scraping, combining the analytical power of `trafilatura` with the elegance of a functional programming interface.

## 📜 How to Cite

If you use PipeScraper in your research or project, please cite it as follows:

### BibTeX

```bibtex
@software{pipescraper2026,
  author = {Mustafa, Yasser},
  title = {PipeScraper: A pipe-based news article scraping and metadata extraction library},
  url = {https://github.com/Yasser03/pipescraper},
  version = {0.3.0},
  year = {2026}
}
```

### APA

Mustafa, Y. (2026). PipeScraper: A pipe-based news article scraping and metadata extraction library (Version 0.3.0) [Computer software]. https://github.com/Yasser03/pipescraper

## �🙏 Acknowledgments

- **[trafilatura](https://github.com/adbar/trafilatura)** — Core content extraction engine
- **[newspaper4k](https://github.com/ahmed精密/newspaper4k/)** — Supplementary time extraction
- **[pipeframe](https://github.com/Yasser03/pipeframe)** — Inspiration for pipe-based syntax
- **[pipeplotly](https://github.com/Yasser03/pipeplotly)** — Pipe pattern implementation reference

## 📧 Contact

For questions, issues, or suggestions, please open an issue on GitHub.

---

**Made with ❤️ by Dr. Yasser Mustafa**

