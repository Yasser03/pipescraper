"""
PipeFrame integration for pipescraper.

This module provides seamless integration with PipeFrame, allowing users to
leverage all PipeFrame verbs (select, filter, mutate, arrange, etc.) in their
pipescraper pipelines.

Example:
    >>> from pipescraper import FetchLinks, ExtractArticles, ToPipeFrame
    >>> from pipeframe import select, filter, arrange
    >>> 
    >>> result = ("https://news.com"
    ...           >> FetchLinks()
    ...           >> ExtractArticles()
    ...           >> ToPipeFrame()
    ...           >> select('title', 'author', 'date_published')
    ...           >> filter(lambda df: df['author'].notna())
    ...           >> arrange('date_published', ascending=False))
"""

import logging
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from pipescraper.core import Article

logger = logging.getLogger(__name__)

# Check if pipeframe is available
try:
    import pipeframe
    # In 0.2.0+, it's DataFrame, not PipeFrame
    from pipeframe import DataFrame as PipeFrame, select, filter
    PIPEFRAME_AVAILABLE = True
    logger.debug("PipeFrame is available")
except ImportError:
    # Try alternate name just in case
    try:
        from pipeframe import PipeFrame, select, filter
        PIPEFRAME_AVAILABLE = True
    except ImportError:
        PIPEFRAME_AVAILABLE = False
        logger.debug("PipeFrame is not installed or broken")
        PipeFrame = None


def check_pipeframe_available() -> bool:
    """
    Check if PipeFrame is available.
    
    Returns:
        True if PipeFrame is installed, False otherwise
    """
    return PIPEFRAME_AVAILABLE


def is_pipeframe(obj) -> bool:
    """
    Check if object is a PipeFrame DataFrame.
    
    Args:
        obj: Object to check
        
    Returns:
        True if object is a PipeFrame instance
    """
    if not PIPEFRAME_AVAILABLE:
        return False
    
    return isinstance(obj, PipeFrame)


def to_pipeframe(df) -> 'PipeFrame':
    """
    Convert pandas DataFrame to PipeFrame.
    
    Args:
        df: pandas DataFrame
        
    Returns:
        PipeFrame DataFrame
        
    Raises:
        ImportError: If PipeFrame is not installed
    """
    if not PIPEFRAME_AVAILABLE:
        raise ImportError(
            "PipeFrame is not installed. Install it with: pip install pipeframe"
        )
    
    import pandas as pd
    
    if is_pipeframe(df):
        return df
    
    if isinstance(df, pd.DataFrame):
        return PipeFrame(df)
    
    raise TypeError(f"Cannot convert {type(df)} to PipeFrame")


def articles_to_pipeframe(articles: List['Article'], include_text: bool = True) -> 'PipeFrame':
    """
    Convert list of Articles directly to PipeFrame.
    
    Args:
        articles: List of Article objects
        include_text: Whether to include the full article text
        
    Returns:
        PipeFrame DataFrame with article data
        
    Raises:
        ImportError: If PipeFrame is not installed
    """
    if not PIPEFRAME_AVAILABLE:
        raise ImportError(
            "PipeFrame is not installed. Install it with: pip install pipeframe"
        )
    
    import pandas as pd
    
    # Define standard columns based on Article.to_dict()
    columns = [
        'url', 'source', 'title', 'text', 'description', 
        'author', 'date_published', 'time_published', 
        'language', 'tags', 'image_url'
    ]
    
    # If not including text, remove it from standard columns
    if not include_text:
        columns.remove('text')
    
    if not articles:
        # Return empty PipeFrame with schema
        return PipeFrame(pd.DataFrame(columns=columns))
    
    # Convert articles to dictionaries
    records = [article.to_dict() for article in articles]
    
    # Create pandas DataFrame
    df = pd.DataFrame(records)
    
    # Ensure all standard columns exist
    for col in columns:
        if col not in df.columns:
            df[col] = None
            
    # Reorder to match standard column order
    df = df[columns]
    
    # Convert to PipeFrame
    return PipeFrame(df)


def get_pipeframe_verbs():
    """
    Get all available PipeFrame verbs safely.
    
    Returns:
        Dictionary of verb names to verb classes
        
    Raises:
        ImportError: If PipeFrame is not installed
    """
    if not PIPEFRAME_AVAILABLE:
        raise ImportError(
            "PipeFrame is not installed. Install it with: pip install pipeframe"
        )
    
    import pipeframe
    
    # Safely collect available verbs
    verbs = {}
    
    # Mapping of name to attribute
    verb_map = {
        'select': 'select',
        'filter': 'filter',
        'mutate': 'mutate',
        'arrange': 'arrange',
        'group_by': 'group_by',
        'summarize': 'summarize',
        'rename': 'rename',
        'distinct': 'distinct',
        'head': 'head',
        'tail': 'tail',
        'sample': 'sample',
        'count': 'count',
        'pull': 'pull',
        'slice': 'slice_rows',
        'drop': 'drop',
        'fill_na': 'fill_na',
        'drop_na': 'drop_na',
        'join': 'join',
        'bind_rows': 'bind_rows',
        'bind_cols': 'bind_cols',
    }
    
    for name, attr in verb_map.items():
        if hasattr(pipeframe, attr):
            verbs[name] = getattr(pipeframe, attr)
            
    return verbs


# Re-export commonly used PipeFrame verbs for convenience
if PIPEFRAME_AVAILABLE:
    # Safely import commonly used verbs
    try:
        from pipeframe import select, mutate, arrange, group_by, summarize, rename, distinct, tail
    except ImportError:
        # Fallback to importing only what's definitely there
        logger.warning("Some PipeFrame verbs could not be imported. Integration may be partial.")
        select = getattr(pipeframe, 'select', None)
        mutate = getattr(pipeframe, 'mutate', None)
        arrange = getattr(pipeframe, 'arrange', None)
        group_by = getattr(pipeframe, 'group_by', None)
        summarize = getattr(pipeframe, 'summarize', None)
        rename = getattr(pipeframe, 'rename', None)
        distinct = getattr(pipeframe, 'distinct', None)
        tail = getattr(pipeframe, 'tail', None)

    # Internal reference to the real pipeframe filter
    _pf_filter = getattr(pipeframe, 'filter', None)
    
    def filter_wrapper(condition):
        """
        A wrapper around pipeframe.filter that supports both string 
        expressions (native pipeframe) and functions (standard pandas/dplyr).
        """
        if isinstance(condition, str):
            # Pass directly to pipeframe if it's a string
            return _pf_filter(condition)
        
        # If it's a function, create a custom pipeable that applies it
        def custom_filter(pf):
            # Access underlying data if it's a pipeframe object
            # In pipeframe 0.2.0+, the underlying data is usually in ._data or it's a pandas-like object
            is_pf = hasattr(pf, '_data')
            df = pf._data if is_pf else pf
            
            import pandas as pd
            try:
                # Try applying it to the whole DF/Series (mask expectation)
                mask = condition(df)
                # Use .loc for safety with masks
                filtered_df = df.loc[mask]
            except Exception:
                # Fallback: Apply row-wise if it's a simple predicate
                filtered_df = df[df.apply(condition, axis=1)]
                
            if is_pf:
                # Return the same type as input (PipeFrame/DataFrame)
                return type(pf)(filtered_df)
            return filtered_df
        
        return custom_filter

    # Export our enhanced filter
    filter_df = filter_wrapper
    # Also export as 'filter' to shadow the native one
    filter = filter_wrapper
    pf_head = getattr(pipeframe, 'head', None)
    sample = getattr(pipeframe, 'sample', None)
    slice_rows = getattr(pipeframe, 'slice_rows', None)

    __all__ = [
        'select',
        'filter_df',
        'mutate',
        'arrange',
        'group_by',
        'summarize',
        'rename',
        'distinct',
        'pf_head',
        'tail',
        'sample',
        'slice_rows',
        'articles_to_pipeframe',
        'to_pipeframe',
        'is_pipeframe',
        'check_pipeframe_available',
        'PIPEFRAME_AVAILABLE',
    ]
else:
    __all__ = [
        'articles_to_pipeframe',
        'to_pipeframe',
        'is_pipeframe',
        'check_pipeframe_available',
        'PIPEFRAME_AVAILABLE',
    ]
