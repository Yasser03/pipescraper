"""
PipePlotly integration for pipescraper.

This module provides seamless integration with PipePlotly, allowing users to
create visualizations directly from their pipescraper pipelines using the
Grammar of Graphics approach.

Example:
    >>> from pipescraper import FetchLinks, ExtractArticles, ToPipeFrame
    >>> from pipeplotly import ggplot, aes, geom_bar, geom_point, labs
    >>> 
    >>> # Create bar chart of articles by source
    >>> ("https://news.com"
    ...  >> FetchLinks()
    ...  >> ExtractArticles()
    ...  >> ToPipeFrame()
    ...  >> ggplot(aes(x='source'))
    ...  >> geom_bar()
    ...  >> labs(title='Articles by Source', x='Source', y='Count'))
    
    >>> # Create scatter plot of article length vs date
    >>> ("https://news.com"
    ...  >> FetchLinks()
    ...  >> ExtractArticles()
    ...  >> ToPipeFrame()
    ...  >> mutate(text_length=lambda df: df['text'].str.len())
    ...  >> ggplot(aes(x='date_published', y='text_length', color='source'))
    ...  >> geom_point()
    ...  >> labs(title='Article Length Over Time', x='Date', y='Text Length'))
"""

import logging
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd

logger = logging.getLogger(__name__)

# Check if pipeplotly is available
try:
    import pipeplotly
    from pipeplotly import Plot as ggplot, PlotState
    # Some versions might have ggplot directly, if not, we use Plot
    try:
        from pipeplotly import aes
    except ImportError:
        # In 0.2.0, aes and geoms might be in verbs
        from pipeplotly.verbs import plot_points as aes # Placeholder for check
    
    PIPEPLOTLY_AVAILABLE = True
    logger.debug("PipePlotly is available")
except ImportError:
    PIPEPLOTLY_AVAILABLE = False
    logger.debug("PipePlotly is not installed or broken")


def check_pipeplotly_available() -> bool:
    """
    Check if PipePlotly is available.
    
    Returns:
        True if PipePlotly is installed, False otherwise
    """
    return PIPEPLOTLY_AVAILABLE


def get_pipeplotly_functions():
    """
    Get all available PipePlotly functions.
    
    Returns:
        Dictionary of function names to functions
        
    Raises:
        ImportError: If PipePlotly is not installed
    """
    if not PIPEPLOTLY_AVAILABLE:
        raise ImportError(
            "PipePlotly is not installed. Install it with: pip install pipeplotly"
        )
    
    import pipeplotly
    
    functions = {
        # Core
        'ggplot': pipeplotly.ggplot,
        'aes': pipeplotly.aes,
        
        # Geoms
        'geom_point': pipeplotly.geom_point,
        'geom_line': pipeplotly.geom_line,
        'geom_bar': pipeplotly.geom_bar,
        'geom_histogram': pipeplotly.geom_histogram,
        'geom_box': pipeplotly.geom_box,
        'geom_violin': pipeplotly.geom_violin,
        'geom_scatter': pipeplotly.geom_scatter,
        'geom_area': pipeplotly.geom_area,
        'geom_heatmap': pipeplotly.geom_heatmap,
        
        # Labels and themes
        'labs': pipeplotly.labs,
        'theme': pipeplotly.theme,
        'theme_minimal': pipeplotly.theme_minimal,
        'theme_dark': pipeplotly.theme_dark,
        
        # Scales
        'scale_x_continuous': pipeplotly.scale_x_continuous,
        'scale_y_continuous': pipeplotly.scale_y_continuous,
        'scale_color_manual': pipeplotly.scale_color_manual,
        
        # Facets
        'facet_wrap': pipeplotly.facet_wrap,
        'facet_grid': pipeplotly.facet_grid,
    }
    
    return functions


# Common visualizations for news article data
def create_articles_by_source_chart(df: 'pd.DataFrame', **kwargs):
    """
    Create a bar chart showing number of articles by source.
    
    Args:
        df: DataFrame with article data
        **kwargs: Additional arguments for customization
        
    Returns:
        Plotly figure
        
    Raises:
        ImportError: If PipePlotly is not installed
    """
    if not PIPEPLOTLY_AVAILABLE:
        raise ImportError(
            "PipePlotly is not installed. Install it with: pip install pipeplotly"
        )
    
    from pipeplotly import ggplot, aes, geom_bar, labs
    
    title = kwargs.get('title', 'Articles by Source')
    
    return (df
            >> ggplot(aes(x='source'))
            >> geom_bar()
            >> labs(title=title, x='Source', y='Article Count'))


def create_articles_timeline(df: 'pd.DataFrame', **kwargs):
    """
    Create a line chart showing articles over time.
    
    Args:
        df: DataFrame with article data (must have date_published)
        **kwargs: Additional arguments for customization
        
    Returns:
        Plotly figure
        
    Raises:
        ImportError: If PipePlotly is not installed
    """
    if not PIPEPLOTLY_AVAILABLE:
        raise ImportError(
            "PipePlotly is not installed. Install it with: pip install pipeplotly"
        )
    
    from pipeplotly import ggplot, aes, geom_line, labs
    import pandas as pd
    
    # Convert date to datetime if needed
    df_copy = df.copy()
    if 'date_published' in df_copy.columns:
        df_copy['date_published'] = pd.to_datetime(df_copy['date_published'])
        df_copy = df_copy.sort_values('date_published')
    
    title = kwargs.get('title', 'Articles Published Over Time')
    
    return (df_copy
            >> ggplot(aes(x='date_published'))
            >> geom_line(stat='count')
            >> labs(title=title, x='Date', y='Article Count'))


def create_text_length_distribution(df: 'pd.DataFrame', **kwargs):
    """
    Create a histogram of article text lengths.
    
    Args:
        df: DataFrame with article data (must have text column)
        **kwargs: Additional arguments for customization
        
    Returns:
        Plotly figure
        
    Raises:
        ImportError: If PipePlotly is not installed
    """
    if not PIPEPLOTLY_AVAILABLE:
        raise ImportError(
            "PipePlotly is not installed. Install it with: pip install pipeplotly"
        )
    
    from pipeplotly import ggplot, aes, geom_histogram, labs
    
    # Add text length column
    df_copy = df.copy()
    df_copy['text_length'] = df_copy['text'].str.len()
    
    title = kwargs.get('title', 'Distribution of Article Lengths')
    bins = kwargs.get('bins', 30)
    
    return (df_copy
            >> ggplot(aes(x='text_length'))
            >> geom_histogram(bins=bins)
            >> labs(title=title, x='Text Length (characters)', y='Count'))


def create_articles_by_language(df: 'pd.DataFrame', **kwargs):
    """
    Create a bar chart showing articles by language.
    
    Args:
        df: DataFrame with article data (must have language column)
        **kwargs: Additional arguments for customization
        
    Returns:
        Plotly figure
        
    Raises:
        ImportError: If PipePlotly is not installed
    """
    if not PIPEPLOTLY_AVAILABLE:
        raise ImportError(
            "PipePlotly is not installed. Install it with: pip install pipeplotly"
        )
    
    from pipeplotly import ggplot, aes, geom_bar, labs
    
    title = kwargs.get('title', 'Articles by Language')
    
    return (df
            >> ggplot(aes(x='language'))
            >> geom_bar()
            >> labs(title=title, x='Language', y='Article Count'))


# Re-export commonly used PipePlotly functions with callable wrappers
if PIPEPLOTLY_AVAILABLE:
    class PipeableWrapper:
        """A wrapper that makes pipeplotly objects callable for PipeFrame compatibility."""
        def __init__(self, inner):
            self.inner = inner
        
        def __call__(self, df):
            # If it's a PipeFrame, use the underlying data to avoid recursion
            data = getattr(df, '_data', df)
            res = data >> self.inner
            # If the result is a Plot, it should stay a Plot (it's the end of a chain or intermediate)
            # However, to be safe for further piping from PipeFrame, we can wrap it
            if hasattr(res, '__rrshift__') and not callable(res):
                return PipeableWrapper(res)
            return res
        
        def __rrshift__(self, df):
            return self.__call__(df)
        
        def __rshift__(self, other):
            other_inner = getattr(other, 'inner', other)
            return PipeableWrapper(self.inner >> other_inner)
            
        def __repr__(self):
            return repr(self.inner)

    def wrap_viz(func):
        """Decorator to wrap a visualization function to return a PipeableWrapper."""
        if func is None:
            return None
        import functools
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            res = func(*args, **kwargs)
            if hasattr(res, '__rrshift__') and not callable(res):
                return PipeableWrapper(res)
            return res
        return wrapper

    from pipeplotly import Plot as _original_ggplot, PlotState
    ggplot = wrap_viz(_original_ggplot)
    
    # Safely import and wrap verbs
    try:
        from pipeplotly.verbs import (
            plot_points as _geom_point,
            plot_lines as _geom_line,
            plot_bars as _geom_bar,
            plot_histogram as _geom_histogram,
            plot_box as _geom_box,
            plot_violin as _geom_violin,
            plot_heatmap as _geom_heatmap,
            add_labels as _labs,
            set_theme as _set_theme,
            show,
        )
        geom_point = wrap_viz(_geom_point)
        geom_line = wrap_viz(_geom_line)
        geom_bar = wrap_viz(_geom_bar)
        geom_histogram = wrap_viz(_geom_histogram)
        geom_box = wrap_viz(_geom_box)
        geom_violin = wrap_viz(_geom_violin)
        geom_heatmap = wrap_viz(_geom_heatmap)
        labs = wrap_viz(_labs)
        set_theme = wrap_viz(_set_theme)
        
        # Aliases for compatibility
        theme_minimal = lambda: set_theme("minimal")
        theme_dark = lambda: set_theme("dark")
        
        # Mock aes if missing, 0.2.0 uses keyword args in verbs
        try:
            from pipeplotly import aes as _aes
            aes = wrap_viz(_aes)
        except ImportError:
            aes = lambda **kwargs: kwargs 
            
    except ImportError:
        # Fallback for other versions if needed
        geom_point = getattr(pipeplotly, 'geom_point', None)
        geom_line = getattr(pipeplotly, 'geom_line', None)
        geom_bar = getattr(pipeplotly, 'geom_bar', None)
        labs = getattr(pipeplotly, 'labs', None)
        aes = getattr(pipeplotly, 'aes', None)
        show = getattr(pipeplotly, 'show', None)

    __all__ = [
        'ggplot',
        'PlotState',
        'geom_point',
        'geom_line',
        'geom_bar',
        'geom_histogram',
        'geom_box',
        'geom_violin',
        'geom_heatmap',
        'labs',
        'theme_minimal',
        'theme_dark',
        'aes',
        'show',
        'create_articles_by_source_chart',
        'create_articles_timeline',
        'create_text_length_distribution',
        'create_articles_by_language',
        'check_pipeplotly_available',
        'PIPEPLOTLY_AVAILABLE',
    ]
else:
    __all__ = [
        'create_articles_by_source_chart',
        'create_articles_timeline',
        'create_text_length_distribution',
        'create_articles_by_language',
        'check_pipeplotly_available',
        'PIPEPLOTLY_AVAILABLE',
    ]
