# 📖 PipeScraper Wiki

Welcome to the official PipeScraper Wiki. This is the comprehensive technical manual and reference guide for the `pipescraper` library.

---

## 📑 Table of Contents
1. [Core Philosophy](#-core-philosophy)
2. [Installation & Setup](#-installation--setup)
3. [Mastering the Pipe `>>`](#-mastering-the-pipe)
4. [Google News: Discovery & Decoding](#-google-news-discovery--decoding)
5. [Extraction Engines](#-extraction-engines)
6. [High-Performance Patterns](#-high-performance-patterns)
7. [Data Science Integrations](#-data-science-integrations)
8. [Advanced Configuration](#-advanced-configuration)
9. [Author & Citation](#-author--citation)

---

## 🎯 Core Philosophy

PipeScraper is designed around **Functional Data Pipeling**. Instead of complex nested objects or callback hell, data flows through concentrated "verbs."

- **Readability**: Code should look like a description of the task.
- **Portability**: Pipelines are objects that can be shared and reused.
- **Speed**: Built-in parallelism for I/O bound extraction tasks.

---

## 📦 Installation & Setup

### Requirements
- Python 3.8+
- `pandas`
- `trafilatura`
- `newspaper4k`
- `gnews`

### Basic Install
```bash
pip install pipescraper
```

### Full Data Science Suite
```bash
pip install "pipescraper[all]"
```
This includes `pipeframe` for manipulation and `pipeplotly` for visualization.

---

## 🔗 Mastering the Pipe `>>`

The `>>` operator in PipeScraper uses the `__rrshift__` magic method. It allows you to chain a **Producer** (like a URL string or `FetchGoogleNews`) to a series of **Transformers** (like `ExtractArticles`) and finally to a **Consumer** (like `ToDataFrame`).

### Example Workflow
```python
from pipescraper import FetchGoogleNews, ExtractArticles, ToDataFrame

# The Producer: FetchGoogleNews
# The Transformer: ExtractArticles
# The Consumer: ToDataFrame
df = (FetchGoogleNews(search="Artificial Intelligence") >> 
      ExtractArticles(workers=10) >> 
      ToDataFrame())
```

---

## 🌍 Google News: Discovery & Decoding

One of the most powerful features of v0.3.0 is the **Mimetic Decoder**.

### The Challenge
Google News URLs (e.g., `news.google.com/rss/articles/...`) redirect to article destinations. However, Google often serves a **Consent Wall** to automated tools.

### The PipeScraper Solution
We use a specialized `GoogleNewsFetcher` that:
1.  **Discovery**: Uses `gnews` and `RSS` to find encoded links.
2.  **Mimicry**: Performs a `batchexecute` POST request mimicking a Chrome browser.
3.  **Authentication**: Uses a hardcoded `SOCS` cookie to signal consent.
4.  **Parallelism**: Decoding 20 URLs sequentially takes ~30s; PipeScraper does it in ~5s using threads.

### Search Aggregation
You can search for multiple topics at once. PipeScraper will run them in parallel and merge the results:
```python
FetchGoogleNews(search=["NVIDIA", "AMD stock", "Intel AI"], max_results=5)
# Returns a single deduplicated list of URLs.
```

---

## 🧪 Extraction Engines

PipeScraper uses a **Dual-Engine Strategy**:

1.  **Trafilatura (Primary)**: Best-in-class main text and metadata extraction.
2.  **Newspaper4k (Supplement)**: Specifically used to extract publication *time*, which Trafilatura often misses.

### Structured Data (The Article Class)
Every extraction results in an `Article` object:
- `url`, `source`, `title`
- `text` (Cleaned body text)
- `description`
- `author`
- `date_published` & `time_published`
- `language`, `tags`, `image_url`

---

## ⚡ High-Performance Patterns

### Batch Processing
Always use the `workers` parameter in `ExtractArticles` for production workflows.
- **Safe**: 3-5 workers.
- **Aggressive**: 10-20 workers (ensure you aren't being rate-limited).

### Persistence
The `SaveAs` verb supports `.csv`, `.json`, `.parquet`, and `.xlsx`. Parquet is recommended for large datasets to preserve types.

---

## 📊 Data Science Integrations

### PipeFrame
Transform your results with dplyr-style syntax:
```python
from pipeframe import select, filter, mutate

df = (articles >> ToPipeFrame() >> 
      mutate(word_count=lambda d: d['text'].str.split().str.len()) >> 
      filter(lambda d: d['word_count'] > 500) >> 
      select('title', 'word_count'))
```

### PipePlotly
Visualizing news trends:
```python
from pipeplotly import ggplot, aes, geom_bar

(df >> ggplot(aes(x='source')) >> geom_bar() >> show())
```

---

## 👨‍💻 Author & Citation

### Author
**Dr. Yasser Mustafa**  
AI & Data Science Specialist  
Newcastle Upon Tyne, UK  
[GitHub.com/Yasser03](https://github.com/Yasser03) | [LinkedIn](https://www.linkedin.com/in/yasser-mustafa-phd-72886344/)

### Citation
```bibtex
@software{pipescraper2026,
  author = {Mustafa, Yasser},
  title = {PipeScraper: High-Performance News Extraction},
  url = {https://github.com/Yasser03/pipescraper},
  version = {0.3.0},
  year = {2026}
}
```

---

**PipeScraper: Making news scraping as easy as natural language.** 🚀
