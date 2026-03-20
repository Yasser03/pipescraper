# pipescraper Quick Start Guide

This guide will get you up and running with pipescraper in 5 minutes.

## 📦 Installation

### From PyPI (when published)

```bash
pip install pipescraper
```

### From Source

```bash
# Clone the repository
git clone https://github.com/Yasser03/pipescraper.git
cd pipescraper

# Install in editable mode
pip install -e .
```

## 🚀 Your First Pipeline

### 1. Import pipescraper

```python
from pipescraper import FetchLinks, ExtractArticles, ToDataFrame, SaveAs
```

### 2. Create a Simple Pipeline

```python
result = ("https://news-site.com" >> 
          FetchLinks(max_links=10) >> 
          ExtractArticles() >> 
          ToDataFrame() >> 
          SaveAs("articles.csv"))

print(f"Scraped {len(result)} articles!")
```

### 3. Google News Search (v0.3.0+)

```python
from pipescraper import FetchGoogleNews, ExtractArticles, ToDataFrame

# Search for multiple topics at once
articles = (FetchGoogleNews(search=["AI news", "latest tech"], max_results=10) >> 
            ExtractArticles(workers=5) >> 
            ToDataFrame())

print(f"Found {len(articles)} articles!")
```

That's it! You've just scraped 10 articles and saved them to CSV.

## 📊 What You Get

Each article contains:

```python
Article(
    url="https://example.com/article",
    source="example.com",
    title="Article Title",
    text="Full article text...",
    description="Article summary",
    author="John Doe",
    date_published="2024-01-15",
    time_published="14:30:00",  # ⭐ Time extraction via newspaper4k
    language="en",
    tags=["tech", "news"],
    image_url="https://example.com/image.jpg"
)
```

## 🎯 Common Patterns

### Filter Articles

```python
# Only English articles with authors
result = ("https://news-site.com" >> 
          FetchLinks(max_links=20) >>
          ExtractArticles() >>
          FilterArticles(lambda a: a.language == 'en') >>
          FilterArticles(lambda a: bool(a.author)) >>
          ToDataFrame() >>
          SaveAs("filtered.csv"))
```

### Limit Results

```python
# Get only the first 5 articles
result = ("https://news-site.com" >> 
          FetchLinks(max_links=50) >>
          ExtractArticles() >>
          LimitArticles(5) >>
          ToDataFrame() >>
          SaveAs("top5.json"))
```

### Turbo Scraping (Parallel)

```python
# Speed up scraping with multiple workers (recommended: 5-10)
result = ("https://news-site.com" >> 
          FetchLinks(max_links=50) >>
          ExtractArticles(workers=5) >>
          ToDataFrame() >>
          SaveAs("fast_results.csv"))

print(f"Turbo Scraped {len(result)} articles in record time!")
```

### Multiple Export Formats

```python
df = ("https://news-site.com" >> 
      FetchLinks(max_links=10) >>
      ExtractArticles() >>
      ToDataFrame())

# Export to different formats
df >> SaveAs("articles.csv")
df >> SaveAs("articles.json")
df >> SaveAs("articles.xlsx")
df >> SaveAs("articles.parquet")
```

### Work with DataFrame Directly

```python
# Get DataFrame for analysis
df = ("https://news-site.com" >> 
      FetchLinks(max_links=20) >>
      ExtractArticles() >>
      ToDataFrame())

# Use pandas operations
print(df.info())
print(df['title'].head())
print(df.describe())

# Sort by date
df_sorted = df.sort_values('date_published', ascending=False)
```

## ⚙️ Configuration

### Be Respectful

```python
# Add delays and respect robots.txt
result = ("https://news-site.com" >> 
          FetchLinks(
              max_links=10,
              respect_robots=True,    # Check robots.txt
              delay=2.0,              # 2s between page requests
              user_agent="MyBot/1.0"  # Identify yourself
          ) >>
          ExtractArticles(delay=2.0) >>  # 2s between articles
          ToDataFrame() >>
          SaveAs("articles.csv"))
```

### Skip Failed Extractions

```python
# Continue even if some articles fail
articles = (urls >> 
            ExtractArticles(
                skip_errors=True,  # Don't raise on failures
                timeout=15         # 15s timeout per article
            ))
```

## 🎓 Next Steps

1. **Read the full documentation** in [README.md](README.md)
2. **Check out examples** in `examples/basic_usage.py`
3. **Run tests** with `pytest tests/`
4. **Contribute** by reading [CONTRIBUTING.md](CONTRIBUTING.md)

## 🆘 Troubleshooting

### Import Errors

```bash
# Make sure all dependencies are installed
pip install -r requirements.txt
```

### No Articles Found

- Check if the URL is correct
- Verify robots.txt allows scraping
- Try increasing `max_links`
- Check your internet connection

### Extraction Failures

- Some websites block scrapers
- Increase `delay` to avoid rate limiting
- Set a proper `user_agent`
- Use `skip_errors=True` to continue on failures

## 📚 Learn More

- **Full Documentation**: [README.md](README.md)
- **API Reference**: See docstrings in `pipescraper/` modules
- **Examples**: `examples/basic_usage.py`
- **Tests**: `tests/test_pipescraper.py` for usage patterns

---

**Happy scraping! 🎉**

