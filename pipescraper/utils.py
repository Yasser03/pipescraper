"""
Utility functions for pipescraper.

This module contains helper functions for URL validation, text processing,
and other common operations.
"""

import re
from urllib.parse import urlparse, urlunparse
from typing import Optional


def is_valid_url(url: str) -> bool:
    """
    Check if a string is a valid URL.
    
    Args:
        url: String to validate
        
    Returns:
        True if valid URL, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_url(url: str) -> str:
    """
    Normalize a URL by removing fragments and normalizing scheme.
    
    Args:
        url: URL to normalize
        
    Returns:
        Normalized URL string
    """
    parsed = urlparse(url)
    
    # Remove fragment
    normalized = urlunparse((
        parsed.scheme.lower(),
        parsed.netloc.lower(),
        parsed.path,
        parsed.params,
        parsed.query,
        ''  # Remove fragment
    ))
    
    # Remove trailing slash if not root
    if normalized.endswith('/') and len(parsed.path) > 1:
        normalized = normalized[:-1]
    
    return normalized


def sanitize_text(text: Optional[str]) -> str:
    """
    Sanitize extracted text by removing extra whitespace and normalizing.
    
    Args:
        text: Text to sanitize
        
    Returns:
        Cleaned text string
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def get_domain(url: str) -> str:
    """
    Extract domain from URL.
    
    Args:
        url: URL to parse
        
    Returns:
        Domain string
    """
    parsed = urlparse(url)
    return parsed.netloc


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length with suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to append if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def clean_author_name(author: str) -> str:
    """
    Clean author name by removing common prefixes.
    
    Args:
        author: Raw author string
        
    Returns:
        Cleaned author name
    """
    if not author:
        return ""
    
    # Remove common prefixes
    prefixes = ['By ', 'by ', 'BY ']
    for prefix in prefixes:
        if author.startswith(prefix):
            author = author[len(prefix):]
    
    return author.strip()
