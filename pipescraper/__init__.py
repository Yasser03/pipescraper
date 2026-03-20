"""
pipescraper: A pipe-based news article scraping and metadata extraction library.

pipescraper provides a natural language verb-based interface for scraping news
websites and extracting structured article metadata using the pipe (>>) operator.

Integrates seamlessly with PipeFrame for data manipulation and PipePlotly for
visualization, enabling complete end-to-end pipelines from scraping to analysis.

Example:
    >>> from pipescraper import FetchLinks, ExtractArticles, ToDataFrame, SaveAs
    >>> ("https://www.bbc.com/news" >>   # Replace with your target URL
    ...  FetchLinks() >> 
    ...  ExtractArticles() >> 
    ...  ToDataFrame() >> 
    ...  SaveAs("articles.csv"))
    
    >>> # With PipeFrame integration
    >>> from pipescraper import FetchLinks, ExtractArticles, ToPipeFrame
    >>> from pipeframe import select, filter, arrange
    >>> ("https://www.bbc.com/news" >>   # Replace with your target URL
    ...  FetchLinks() >> 
    ...  ExtractArticles() >> 
    ...  ToPipeFrame() >>
    ...  select('title', 'author', 'date_published') >>
    ...  filter(lambda df: df['author'].notna()) >>
    ...  arrange('date_published', ascending=False))

Author: pipescraper Contributors
License: MIT
"""

__version__ = "0.3.0"
__author__ = "pipescraper Contributors"
__license__ = "MIT"

from pipescraper.pipes import (
    FetchLinks,
    ExtractArticles,
    ToDataFrame,
    ToPipeFrame,
    SaveAs,
    FilterArticles,
    LimitArticles,
    WithDelay,
    Deduplicate,
    FetchGoogleNews,
)

from pipescraper.core import (
    Article,
    ArticleExtractor,
    LinkFetcher,
    GoogleNewsFetcher,
)

# Import integration modules
from pipescraper.pipeframe_integration import (
    PIPEFRAME_AVAILABLE,
    check_pipeframe_available,
)

from pipescraper.pipeplotly_integration import (
    PIPEPLOTLY_AVAILABLE,
    check_pipeplotly_available,
)

# Conditionally export PipeFrame verbs if available
if PIPEFRAME_AVAILABLE:
    import pipescraper.pipeframe_integration as pf_int
    
    # Safely import each verb, only if it's not None
    select = getattr(pf_int, 'select', None)
    filter_df = getattr(pf_int, 'filter_df', None)
    filter = getattr(pf_int, 'filter', None)
    mutate = getattr(pf_int, 'mutate', None)
    arrange = getattr(pf_int, 'arrange', None)
    group_by = getattr(pf_int, 'group_by', None)
    summarize = getattr(pf_int, 'summarize', None)
    rename = getattr(pf_int, 'rename', None)
    distinct = getattr(pf_int, 'distinct', None)
    pf_head = getattr(pf_int, 'pf_head', None)
    tail = getattr(pf_int, 'tail', None)
    sample = getattr(pf_int, 'sample', None)
    slice_rows = getattr(pf_int, 'slice_rows', None)

# Conditionally export PipePlotly functions if available
if PIPEPLOTLY_AVAILABLE:
    from pipescraper.pipeplotly_integration import (
        ggplot,
        aes,
        geom_point,
        geom_line,
        geom_bar,
        geom_histogram,
        geom_box,
        geom_violin,
        geom_heatmap,
        labs,
        set_theme,
        theme_minimal,
        theme_dark,
        show,
        create_articles_by_source_chart,
        create_articles_timeline,
        create_text_length_distribution,
        create_articles_by_language,
    )

__all__ = [
    # Pipe verbs
    "FetchLinks",
    "ExtractArticles",
    "ToDataFrame",
    "ToPipeFrame",
    "SaveAs",
    "FilterArticles",
    "LimitArticles",
    "WithDelay",
    "Deduplicate",
    "FetchGoogleNews",
    # Core classes
    "Article",
    "ArticleExtractor",
    "LinkFetcher",
    "GoogleNewsFetcher",
    # Integration flags
    "PIPEFRAME_AVAILABLE",
    "PIPEPLOTLY_AVAILABLE",
    "check_pipeframe_available",
    "check_pipeplotly_available",
]

# Add PipeFrame verbs to __all__ if they are available and not None
if PIPEFRAME_AVAILABLE:
    for verb in [
        "select", "filter_df", "filter", "mutate", "arrange", "group_by", 
        "summarize", "rename", "distinct", "pf_head", "tail", 
        "sample", "slice_rows"
    ]:
        if globals().get(verb) is not None:
            __all__.append(verb)

# Add PipePlotly functions to __all__ if available
if PIPEPLOTLY_AVAILABLE:
    __all__.extend([
        "ggplot",
        "aes",
        "geom_point",
        "geom_line",
        "geom_bar",
        "geom_histogram",
        "geom_box",
        "geom_violin",
        "geom_heatmap",
        "labs",
        "theme_minimal",
        "theme_dark",
        "show",
        "create_articles_by_source_chart",
        "create_articles_timeline",
        "create_text_length_distribution",
        "create_articles_by_language",
    ])
