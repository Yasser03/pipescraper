# PipeScraper 🔗

**A pipe-based news article scraping and metadata extraction library for Python**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

pipescraper provides a natural language verb-based interface for scraping news websites and extracting structured article metadata using the intuitive pipe (`>>`) operator. Built on top of [trafilatura](https://github.com/adbar/trafilatura) with supplementary time extraction via [newspaper4k](https://github.com/AndyTheFactory/newspaper4k), pipescraper combines powerful extraction capabilities with an elegant, chainable API.

```python
from pipescraper import *

# Your scraping pipeline reads like a story
result = ("https://www.bbc.com/news"   # Replace with your target URL
    >> FetchLinks(max_links=10) 
    >> ExtractArticles() 
    >> FilterArticles(lambda a: a.language == 'en')
    >> ToDataFrame() 
    >> SaveAs("articles.csv")
)
```

> **💡 How to read `>>`:** Read the `>>` operator as **"pipe to"** or **"then"**. For example, the code above reads as: *"Take the URL, **then** fetch links, **then** extract articles, **then** filter for English articles... "*

---

## 🌟 Why pipescraper?

### **Readability First**

```python
# ❌ Traditional logic is nested, hard to read, and error-prone
urls = fetch_links("https://www.bbc.com/news", max_links=10)  # Replace with your target URL
articles = []
for url in urls:
    time.sleep(1)
    art = extract_article(url)
    if art.language == 'en' and art.author:
        articles.append(art)
save_to_csv(articles, "articles.csv")

# ✅ pipescraper: Clear and intuitive
("https://www.bbc.com/news"   # Replace with your target URL
    >> FetchLinks(max_links=10) 
    >> ExtractArticles(delay=1.0) 
    >> FilterArticles(lambda a: a.language == 'en' and bool(a.author)) 
    >> ToDataFrame() 
    >> SaveAs("articles.csv")
)
```

### **Key Features**

- 🔗 **Pipe-based syntax** — Chain operations naturally with the `>>` operator
- 📰 **Comprehensive metadata extraction** — Extract URL, source, title, text, author, dates, language, and more
- ⏰ **Publication time parsing** — Supplement trafilatura's date extraction with full timestamp support
- 🤖 **Respectful scraping** — Built-in robots.txt compliance and request throttling
- 🌐 **Google News Search** — Search for keywords or sentences across regions and time periods ⭐ NEW
- 🧠 **Automatic URL Decoding** — Parallel `batchexecute` decoder for Google News (bypasses consent wall) ⭐ NEW
- 📊 **Pandas integration** — Export to DataFrame with CSV, JSON, Excel support
- 🎯 **Flexible filtering** — Filter articles by language, author, content length, or custom criteria
- 🧹 **Automatic deduplication** — Remove duplicate articles by URL
- ⚡ **Parallel Scraping** — Turbocharge batch extraction with multi-threaded workers
- 🔧 **PipeFrame integration** — Use all PipeFrame verbs (select, filter, mutate, arrange, etc.) for data manipulation
- 📈 **PipePlotly integration** — Create visualizations with Grammar of Graphics using ggplot, geom_bar, geom_point, etc.

---

## 🚀 Quick Start

### Installation

```bash
# Basic installation
pip install pipescraper

# Install with all optional integrations (PipeFrame & PipePlotly)
pip install pipescraper[all]
```

Or install from source:

```bash
git clone https://github.com/Yasser03/pipescraper.git
cd pipescraper
pip install -e .
```

### Hello pipescraper!

```python
from pipescraper import FetchLinks, ExtractArticles, ToDataFrame, SaveAs

# Simple pipeline: URL → Links → Articles → DataFrame → CSV
df = ("https://www.bbc.com/news"   # Replace with your target URL
      >> FetchLinks(max_links=10) 
      >> ExtractArticles() 
      >> ToDataFrame() 
      >> SaveAs("articles.csv"))

print(f"Scraped {len(df)} articles successfully! 🎉")
```

---

## 📚 Core Concepts

### The Pipe Operator `>>`

Chain operations naturally without nested function calls or loops:

```python
# PipeScraper approach (reads like a recipe)
articles = ("https://www.bbc.com/news"  # Replace with your target URL
    >> FetchLinks(max_links=20)
    >> ExtractArticles(skip_errors=True)
    >> Deduplicate()
    >> LimitArticles(10)
)
```

### Core Verbs

| Verb | Purpose | Example |
|------|---------|---------|
| `FetchLinks()` | Fetch article links from a base URL | `>> FetchLinks(max_links=50, delay=1.0)` |
| `ExtractArticles()` | Extract metadata from urls | `>> ExtractArticles(workers=5, extract_time=True)` |
| `FetchGoogleNews()` | Search Google News | `>> FetchGoogleNews(search="SpaceX", period="1d")` |
| `FilterArticles()` | Filter by criteria | `>> FilterArticles(lambda a: a.language == 'en')` |
| `LimitArticles()` | Limit number of articles | `>> LimitArticles(10)` |
| `Deduplicate()` | Remove duplicates | `>> Deduplicate()` |
| `ToDataFrame()` | Convert to DataFrame | `>> ToDataFrame(include_text=True)` |
| `ToPipeFrame()` | Convert to PipeFrame | `>> ToPipeFrame()` |
| `SaveAs()` | Save to file | `>> SaveAs("output.csv")` |

---

## 🔥 Advanced Features

### Google News Integration & Decoding

Search for specific topics from Google News, leveraging a high-performance parallel decoder that resolves consent-gated URLs automatically.

```python
# Search for multiple related topics
search_articles = (FetchGoogleNews(
                        search=["latest AI breakthroughs", "quantum computing news"],
                        period="7d",
                        max_results=20) 
                   >> ExtractArticles(workers=5) 
                   >> ToDataFrame())
```

### Turbo Parallel Pipeline

Scrape safely and heavily concurrently using multi-threaded workers.

```python
# Scrape 50 articles in parallel using 10 workers
df = ("https://www.bbc.com/news"   # Replace with your target URL
      >> FetchLinks(max_links=50) 
      >> ExtractArticles(workers=10) 
      >> ToDataFrame())
```

### Extracted Metadata Fields

Each article contains the following fields:

| Field            | Description                   | Source                    |
| ---------------- | ----------------------------- | ------------------------- |
| `url`            | Article URL                   | Input                     |
| `source`         | Domain/source name            | Parsed                    |
| `title`          | Article headline              | Trafilatura / newspaper4k |
| `text`           | Main article content          | Trafilatura               |
| `description`    | Article summary               | Trafilatura               |
| `author`         | Author name(s)                | Trafilatura / newspaper4k |
| `date_published` | Publication date (YYYY-MM-DD) | Trafilatura / newspaper4k |
| `time_published` | Publication time (HH:MM:SS)   | **newspaper4k** ⭐         |
| `language`       | Language code (e.g., 'en')    | Trafilatura               |
| `tags`           | Article tags/categories       | Trafilatura               |
| `image_url`      | Main article image            | Trafilatura / newspaper4k |

⭐ **Note**: `time_published` is extracted via newspaper4k to supplement trafilatura, which only provides dates.

### Data Manipulation & Visualization

Install PipeFrame (`pip install pipescraper[pipeframe]`) and PipePlotly (`pip install pipescraper[pipeplotly]`) for seamless end-to-end pipelines:

```python
from pipescraper import ExtractArticles, ToPipeFrame
from pipeframe import filter, arrange, group_by, summarize
from pipeplotly import ggplot, aes, geom_bar, theme_minimal

# Full Pipeline: Scrape -> Mutate -> Group -> Plot
fig = ("https://www.bbc.com/news"   # Replace with your target URL
       >> FetchLinks(max_links=20) 
       >> ExtractArticles() 
       >> ToPipeFrame() 
       >> filter(lambda df: df['author'].notna())
       >> arrange('date_published', ascending=False)
       >> ggplot(aes(x='source')) 
       >> geom_bar() 
       >> theme_minimal())

fig.show()
```

---

## 🎯 Real-World Examples

### Respectful Scrape & Filter

Configure delays and robots.txt compliance.

```python
result = ("https://www.bbc.com/news"   # Replace with your target URL
          >> FetchLinks(
              max_links=50,
              respect_robots=True,
              delay=3.0,
              user_agent="MyBot/1.0 (contact@example.com)"
          ) 
          >> ExtractArticles(delay=2.0)
          >> FilterArticles(lambda a: a.language == 'en' and bool(a.author))
          >> LimitArticles(20)
          >> Deduplicate()
          >> ToDataFrame(include_text=False)
          >> SaveAs("respectful_scrape.csv"))
```

### Direct Article Extraction

Extract from a specific URL or list of URLs without link discovery.

```python
df = ("https://www.bbc.com/news/specific-article"   # Replace with your target URL
      >> ExtractArticles() 
      >> ToDataFrame() 
      >> SaveAs("single_article.json"))
```

---

## 🆚 Feature Comparison

### pipescraper vs. Trafilatura

| Feature | pipescraper | Trafilatura |
|---------|-------------|-------------|
| Content extraction | ✅ (via trafilatura) | ✅ |
| Metadata extraction | ✅ Enhanced | ✅ Basic |
| Publication time | ✅ (via newspaper4k) | ❌ (date only) |
| Pipe syntax | ✅ | ❌ |
| Link discovery | ✅ | ❌ |
| Batch / Parallel | ✅ | Manual |
| DataFrame export | ✅ (CSV/JSON/Excel)| ❌ |
| Google News Filter | ✅ | ❌ |

**Design Decision:** pipescraper uses a **dual-engine approach**. Trafilatura provides industry-leading content extraction, while newspaper4k complements it by capturing the exact `time_published`, ensuring complete temporal metadata.

---

## 🎓 Learning Resources

- **[Tutorial Notebook](Tutorial.ipynb)** - A complete, hands-on, end-to-end walkthrough
- **[API Reference](API_REFERENCE.md)** - Detailed core documentation
- **[Examples](examples/)** - More advanced usage examples
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

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

---

## 🌟 Star History

If PipeScraper helps your work, please consider giving it a star! ⭐

---

## 📜 How to Cite

If you use PipeScraper in your research or project, please cite it as follows:

```bibtex
@software{pipescraper2026,
  author = {Mustafa, Yasser},
  title = {PipeScraper: A pipe-based news article scraping and metadata extraction library},
  url = {https://github.com/Yasser03/pipescraper},
  version = {0.3.0},
  year = {2026}
}
```

---

## 🙏 Acknowledgments

- **[trafilatura](https://github.com/adbar/trafilatura)** — Core content extraction engine
- **[newspaper4k](https://github.com/AndyTheFactory/newspaper4k)** — Supplementary time extraction
- **[pipeframe](https://github.com/Yasser03/pipeframe)** — Inspiration for pipe-based syntax
- **[pipeplotly](https://github.com/Yasser03/pipeplotly)** — Pipe pattern implementation reference

---

## 💬 Community

- **Issues**: Report bugs or request features
- **Discussions**: Ask questions, share use cases

**Made with ❤️ by Dr. Yasser Mustafa**
