# PipeFrame & PipePlotly Integration Guide

This guide explains how to use pipescraper with PipeFrame for data manipulation and PipePlotly for visualization, creating powerful end-to-end pipelines.

## 📦 Installation

### Install with PipeFrame Support

```bash
pip install pipescraper[pipeframe]
```

### Install with PipePlotly Support

```bash
pip install pipescraper[pipeplotly]
```

### Install Everything

```bash
pip install pipescraper[all]
```

## 🔧 PipeFrame Integration

PipeFrame provides dplyr-style data manipulation verbs for pandas DataFrames. pipescraper integrates seamlessly with all PipeFrame functionality.

### Available PipeFrame Verbs

All PipeFrame verbs can be imported directly from `pipescraper` or from `pipeframe`:

| Verb         | Purpose               | Example                                            |
| ------------ | --------------------- | -------------------------------------------------- |
| `select`     | Select columns        | `select('title', 'author')`                        |
| `filter`     | Filter rows           | `filter(lambda df: df['author'].notna())`          |
| `mutate`     | Create/modify columns | `mutate(text_len=lambda df: df['text'].str.len())` |
| `arrange`    | Sort rows             | `arrange('date_published', ascending=False)`       |
| `group_by`   | Group data            | `group_by('source')`                               |
| `summarize`  | Aggregate data        | `summarize(count=('title', 'count'))`              |
| `rename`     | Rename columns        | `rename({'old_name': 'new_name'})`                 |
| `distinct`   | Remove duplicates     | `distinct()`                                       |
| `head`       | First N rows          | `head(10)`                                         |
| `tail`       | Last N rows           | `tail(10)`                                         |
| `sample`     | Random sample         | `sample(n=5)`                                      |
| `count`      | Count rows            | `count()`                                          |
| `pull`       | Extract column        | `pull('title')`                                    |
| `slice_rows` | Slice rows            | `slice_rows(0, 10)`                                |
| `drop`       | Drop columns          | `drop('text')`                                     |
| `fill_na`    | Fill missing values   | `fill_na({'author': 'Unknown'})`                   |
| `drop_na`    | Drop missing values   | `drop_na(subset=['author'])`                       |
| `join`       | Join DataFrames       | `join(other_df, on='url')`                         |
| `bind_rows`  | Concatenate rows      | `bind_rows(df1, df2)`                              |
| `bind_cols`  | Concatenate columns   | `bind_cols(df1, df2)`                              |

### Basic Example

```python
from pipescraper import FetchLinks, ExtractArticles, ToPipeFrame
from pipeframe import select, filter, arrange

result = ("https://www.bbc.com/news" >>   # Replace with your target URL
          FetchLinks(max_links=20) >>
          ExtractArticles() >>
          ToPipeFrame() >>
          select('title', 'author', 'date_published') >>
          filter(lambda df: df['author'].notna()) >>
          arrange('date_published', ascending=False))
```

### Data Transformation Example

```python
from pipescraper import FetchLinks, ExtractArticles, ToPipeFrame, SaveAs
from pipeframe import select, mutate, filter, arrange

result = ("https://www.bbc.com/news" >>   # Replace with your target URL
          FetchLinks(max_links=30) >>
          ExtractArticles() >>
          ToPipeFrame() >>
          mutate(
              text_length=lambda df: df['text'].str.len(),
              title_length=lambda df: df['title'].str.len(),
              has_author=lambda df: df['author'].notna(),
              word_count=lambda df: df['text'].str.split().str.len()
          ) >>
          select('title', 'author', 'source', 'date_published',
                 'text_length', 'word_count', 'has_author') >>
          filter(lambda df: df['word_count'] > 100) >>
          arrange('word_count', ascending=False) >>
          SaveAs('processed_articles.csv'))

print(f"Processed {len(result)} articles")
```

### Aggregation Example

```python
from pipescraper import FetchLinks, ExtractArticles, ToPipeFrame
from pipeframe import group_by, summarize, mutate, arrange

summary = ("https://www.bbc.com/news" >>   # Replace with your target URL
           FetchLinks(max_links=50) >>
           ExtractArticles() >>
           ToPipeFrame() >>
           mutate(text_length=lambda df: df['text'].str.len()) >>
           group_by('source') >>
           summarize(
               article_count=('title', 'count'),
               avg_text_length=('text_length', 'mean'),
               total_words=('text_length', 'sum')
           ) >>
           arrange('article_count', ascending=False))

print(summary)
```

## 📈 PipePlotly Integration

PipePlotly provides Grammar of Graphics-style visualizations using Plotly. Create publication-ready charts directly from your pipescraper pipelines.

### Available PipePlotly Functions

All PipePlotly functions can be imported directly from `pipescraper` or from `pipeplotly`:

#### Core Functions
- `ggplot(aes)` — Initialize plot with aesthetics
- `aes(x, y, color, fill, ...)` — Map data to visual properties

#### Geoms (Geometric Objects)
- `geom_point()` — Scatter plot
- `geom_line()` — Line chart
- `geom_bar()` — Bar chart
- `geom_histogram()` — Histogram
- `geom_box()` — Box plot
- `geom_violin()` — Violin plot
- `geom_scatter()` — Enhanced scatter plot
- `geom_area()` — Area chart
- `geom_heatmap()` — Heatmap

#### Labels and Themes
- `labs(title, x, y, ...)` — Add labels
- `theme()` — Customize theme
- `theme_minimal()` — Minimal theme
- `theme_dark()` — Dark theme

#### Scales
- `scale_x_continuous()` — Customize x-axis scale
- `scale_y_continuous()` — Customize y-axis scale
- `scale_color_manual()` — Manual color mapping

#### Facets
- `facet_wrap()` — Wrap facets
- `facet_grid()` — Grid of facets

### Basic Visualization

```python
from pipescraper import FetchLinks, ExtractArticles, ToPipeFrame
from pipeplotly import ggplot, aes, geom_bar, labs, theme_minimal

fig = ("https://www.bbc.com/news" >>   # Replace with your target URL
       FetchLinks(max_links=20) >>
       ExtractArticles() >>
       ToPipeFrame(include_text=False) >>
       ggplot(aes(x='source')) >>
       geom_bar() >>
       labs(title='Articles by Source', x='Source', y='Count') >>
       theme_minimal())

fig.show()
```

### Scatter Plot with Transformations

```python
from pipescraper import FetchLinks, ExtractArticles, ToPipeFrame
from pipeframe import mutate, filter
from pipeplotly import ggplot, aes, geom_point, labs, theme_minimal

fig = ("https://www.bbc.com/news" >>   # Replace with your target URL
       FetchLinks(max_links=30) >>
       ExtractArticles() >>
       ToPipeFrame() >>
       mutate(
           text_length=lambda df: df['text'].str.len(),
           title_length=lambda df: df['title'].str.len()
       ) >>
       filter(lambda df: df['text_length'] > 0) >>
       ggplot(aes(x='title_length', y='text_length', color='source')) >>
       geom_point() >>
       labs(
           title='Article Title Length vs Text Length',
           x='Title Length (characters)',
           y='Text Length (characters)'
       ) >>
       theme_minimal())

fig.show()
```

### Timeline Visualization

```python
from pipescraper import FetchLinks, ExtractArticles, ToPipeFrame
from pipeframe import filter, mutate
from pipeplotly import ggplot, aes, geom_line, labs
import pandas as pd

fig = ("https://www.bbc.com/news" >>   # Replace with your target URL
       FetchLinks(max_links=50) >>
       ExtractArticles() >>
       ToPipeFrame(include_text=False) >>
       filter(lambda df: df['date_published'].notna()) >>
       mutate(date=lambda df: pd.to_datetime(df['date_published'])) >>
       ggplot(aes(x='date')) >>
       geom_line(stat='count') >>
       labs(
           title='Articles Published Over Time',
           x='Publication Date',
           y='Number of Articles'
       ))

fig.show()
```

### Built-in Helper Visualizations

pipescraper includes pre-built visualization functions for common use cases:

```python
from pipescraper import (
    FetchLinks,
    ExtractArticles,
    ToPipeFrame,
    create_articles_by_source_chart,
    create_text_length_distribution,
    create_articles_by_language,
    create_articles_timeline
)

# Get data
data = ("https://www.bbc.com/news" >>   # Replace with your target URL
        FetchLinks(max_links=30) >>
        ExtractArticles() >>
        ToPipeFrame())

# Create visualizations
fig1 = create_articles_by_source_chart(data, title='Source Distribution')
fig2 = create_text_length_distribution(data, bins=25)
fig3 = create_articles_by_language(data)
fig4 = create_articles_timeline(data)

# Display
fig1.show()
fig2.show()
fig3.show()
fig4.show()
```

## 🚀 Complete End-to-End Example

Here's a complete pipeline that scrapes, transforms, visualizes, and saves:

```python
from pipescraper import (
    FetchLinks,
    ExtractArticles,
    ToPipeFrame,
    SaveAs,
    create_articles_by_source_chart
)
from pipeframe import select, filter, mutate, arrange, group_by, summarize

# 1. Scrape and Transform (Google News Search)
data = (FetchGoogleNews(search="renewable energy breakthroughs", period="7d", max_results=30) >> 
        ExtractArticles(workers=5, delay=0.5) >>
        ToPipeFrame() >>
        mutate(
            text_length=lambda df: df['text'].str.len(),
            word_count=lambda df: df['text'].str.split().str.len(),
            has_author=lambda df: df['author'].notna()
        ) >>
        filter(lambda df: df['word_count'] > 100) >>
        select('title', 'author', 'source', 'date_published',
               'text_length', 'word_count'))

# 2. Save Processed Data
data >> SaveAs('processed_articles.csv')

# 3. Create Summary Statistics
summary = (data >>
           group_by('source') >>
           summarize(
               article_count=('title', 'count'),
               avg_words=('word_count', 'mean'),
               total_articles=('title', 'size')
           ) >>
           arrange('article_count', ascending=False))

summary >> SaveAs('article_summary.csv')

# 4. Create Visualization
fig = create_articles_by_source_chart(
    data,
    title='Article Distribution by News Source'
)
fig.show()

# Print results
print(f"Total articles processed: {len(data)}")
print(f"Average word count: {data['word_count'].mean():.0f}")
print(f"Number of sources: {summary.shape[0]}")
```

## 💡 Best Practices

### 1. Use ToPipeFrame for Data Manipulation

If you're doing any data transformation, use `ToPipeFrame()` instead of `ToDataFrame()`:

```python
# Good - uses PipeFrame
result = (articles >> 
          ToPipeFrame() >>
          select('title', 'author') >>
          filter(lambda df: df['author'].notna()))

# Less optimal - converts to pandas then manually transforms
result = (articles >> 
          ToDataFrame())
result = result[['title', 'author']]
result = result[result['author'].notna()]
```

### 2. Exclude Text for Better Performance

Large text fields can slow down transformations and visualizations:

```python
# Exclude text when not needed
data = (articles >> 
        ToPipeFrame(include_text=False) >>
        ggplot(aes(x='source')) >>
        geom_bar())
```

### 3. Chain Mutate Operations

Multiple `mutate()` calls can be chained for clarity:

```python
data = (articles >>
        ToPipeFrame() >>
        mutate(text_length=lambda df: df['text'].str.len()) >>
        mutate(is_long=lambda df: df['text_length'] > 1000))
```

### 4. Use Helper Functions for Common Visualizations

Built-in helpers save time for standard charts:

```python
# Instead of building from scratch
fig = create_articles_by_source_chart(data)

# vs manual construction
fig = (data >>
       ggplot(aes(x='source')) >>
       geom_bar() >>
       labs(title='Articles by Source'))
```

## 🔍 Checking Integration Availability

Check if integrations are available before using:

```python
from pipescraper import PIPEFRAME_AVAILABLE, PIPEPLOTLY_AVAILABLE

if PIPEFRAME_AVAILABLE:
    print("PipeFrame is installed")
    from pipeframe import select, filter
else:
    print("Install PipeFrame: pip install pipeframe")

if PIPEPLOTLY_AVAILABLE:
    print("PipePlotly is installed")
    from pipeplotly import ggplot, aes
else:
    print("Install PipePlotly: pip install pipeplotly")
```

## 📚 Additional Resources

- **PipeFrame Documentation**: https://github.com/Yasser03/pipeframe
- **PipePlotly Documentation**: https://github.com/Yasser03/pipeplotly
- **pipescraper Examples**: See `examples/advanced_integration.py`

## ❓ Troubleshooting

### ImportError: No module named 'pipeframe'

```bash
pip install pipescraper[pipeframe]
```

### ImportError: No module named 'pipeplotly'

```bash
pip install pipescraper[pipeplotly]
```

### AttributeError when using PipeFrame verbs

Make sure you're using `ToPipeFrame()` instead of `ToDataFrame()`:

```python
# Correct
result = articles >> ToPipeFrame() >> select('title')

# Wrong - ToDataFrame returns pandas, not PipeFrame
result = articles >> ToDataFrame() >> select('title')  # Error!
```

---

**Happy data wrangling and visualization! 📊✨**

