"""
Basic usage examples for pipescraper.

This script demonstrates various ways to use pipescraper's pipe-based syntax
for scraping and extracting news article metadata.
"""

from pipescraper import (
    FetchLinks,
    ExtractArticles,
    ToDataFrame,
    SaveAs,
    FilterArticles,
    LimitArticles,
    Deduplicate,
)


def example_1_basic_pipeline():
    """
    Example 1: Basic pipeline from URL to CSV.
    
    This demonstrates the simplest use case: fetch links from a news site,
    extract article metadata, and save to CSV.
    """
    print("Example 1: Basic Pipeline")
    print("-" * 50)
    
    # Replace with an actual news website URL
    base_url = "https://news.ycombinator.com"
    
    try:
        result = (base_url >> 
                  FetchLinks(max_links=5) >>
                  ExtractArticles(delay=2.0) >>
                  ToDataFrame() >>
                  SaveAs("output/articles_basic.csv"))
        
        print(f"✓ Scraped and saved {len(result)} articles")
        print(f"✓ Output: output/articles_basic.csv")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_2_filtered_pipeline():
    """
    Example 2: Pipeline with filtering.
    
    This demonstrates filtering articles based on criteria (e.g., only
    articles with authors, specific language, etc.).
    """
    print("Example 2: Filtered Pipeline")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        result = (base_url >> 
                  FetchLinks(max_links=10) >>
                  ExtractArticles() >>
                  FilterArticles(lambda a: bool(a.author)) >>  # Only with authors
                  FilterArticles(lambda a: a.language == 'en') >>  # English only
                  ToDataFrame() >>
                  SaveAs("output/articles_filtered.csv"))
        
        print(f"✓ Filtered and saved {len(result)} articles")
        print(f"✓ Output: output/articles_filtered.csv")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_3_limited_pipeline():
    """
    Example 3: Pipeline with limits.
    
    This demonstrates limiting the number of articles at various stages.
    """
    print("Example 3: Limited Pipeline")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        result = (base_url >> 
                  FetchLinks(max_links=20) >>
                  ExtractArticles() >>
                  LimitArticles(5) >>  # Keep only first 5
                  ToDataFrame() >>
                  SaveAs("output/articles_limited.json"))  # Save as JSON
        
        print(f"✓ Limited to {len(result)} articles")
        print(f"✓ Output: output/articles_limited.json")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_4_deduplication():
    """
    Example 4: Pipeline with deduplication.
    
    This demonstrates removing duplicate articles by URL.
    """
    print("Example 4: Deduplication")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        result = (base_url >> 
                  FetchLinks(max_links=15) >>
                  ExtractArticles() >>
                  Deduplicate() >>  # Remove duplicates
                  ToDataFrame() >>
                  SaveAs("output/articles_unique.csv"))
        
        print(f"✓ Deduplicated to {len(result)} unique articles")
        print(f"✓ Output: output/articles_unique.csv")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_5_excel_output():
    """
    Example 5: Save to Excel format.
    
    This demonstrates saving to Excel with metadata intact.
    """
    print("Example 5: Excel Output")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        result = (base_url >> 
                  FetchLinks(max_links=10) >>
                  ExtractArticles() >>
                  ToDataFrame(include_text=False) >>  # Exclude text for smaller file
                  SaveAs("output/articles.xlsx"))
        
        print(f"✓ Saved {len(result)} articles to Excel")
        print(f"✓ Output: output/articles.xlsx")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_6_direct_url_extraction():
    """
    Example 6: Extract from a single URL.
    
    This demonstrates extracting metadata from a specific article URL
    without fetching links first.
    """
    print("Example 6: Direct URL Extraction")
    print("-" * 50)
    
    # Replace with an actual article URL
    article_url = "https://example.com/article"
    
    try:
        result = (article_url >>
                  ExtractArticles() >>
                  ToDataFrame() >>
                  SaveAs("output/single_article.csv"))
        
        print(f"✓ Extracted {len(result)} article")
        print(f"✓ Output: output/single_article.csv")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_7_custom_filtering():
    """
    Example 7: Custom filtering with multiple conditions.
    
    This demonstrates advanced filtering based on date, length, etc.
    """
    print("Example 7: Custom Filtering")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        # Complex filter: articles with text > 500 chars and published date
        result = (base_url >> 
                  FetchLinks(max_links=15) >>
                  ExtractArticles() >>
                  FilterArticles(lambda a: len(a.text) > 500) >>
                  FilterArticles(lambda a: bool(a.date_published)) >>
                  ToDataFrame() >>
                  SaveAs("output/articles_custom.csv"))
        
        print(f"✓ Custom filtered to {len(result)} articles")
        print(f"✓ Output: output/articles_custom.csv")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_8_inspect_dataframe():
    """
    Example 8: Inspect DataFrame before saving.
    
    This demonstrates working with the DataFrame directly.
    """
    print("Example 8: Inspect DataFrame")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        df = (base_url >> 
              FetchLinks(max_links=5) >>
              ExtractArticles() >>
              ToDataFrame())
        
        print(f"✓ Extracted {len(df)} articles")
        print(f"\nDataFrame Info:")
        print(df.info())
        print(f"\nFirst few rows:")
        print(df.head())
        
        # Can now use standard pandas operations
        df_sorted = df.sort_values('date_published', ascending=False)
        print(f"\nSorted by date (most recent first):")
        print(df_sorted[['title', 'date_published']].head())
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_9_respecting_robots():
    """
    Example 9: Configure robots.txt and delay settings.
    
    This demonstrates being a good web citizen with proper throttling.
    """
    print("Example 9: Respectful Scraping")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        result = (base_url >> 
                  FetchLinks(
                      max_links=5,
                      respect_robots=True,  # Respect robots.txt
                      delay=3.0,  # 3 second delay between requests
                  ) >>
                  ExtractArticles(delay=3.0) >>  # Also delay article extraction
                  ToDataFrame() >>
                  SaveAs("output/articles_respectful.csv"))
        
        print(f"✓ Respectfully scraped {len(result)} articles")
        print(f"✓ Output: output/articles_respectful.csv")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_11_turbo_scraping():
    """
    Example 11: Turbo Parallel Scraping (v0.2.1+).
    
    This demonstrates using the 'workers' parameter to speed up 
    batch article extraction.
    """
    import time
    print("Example 11: Turbo Scraping (Parallel)")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        start_time = time.time()
        # Use 10 parallel workers for extraction
        result = (base_url >> 
                  FetchLinks(max_links=10) >>
                  ExtractArticles(workers=10) >>
                  ToDataFrame() >>
                  SaveAs("output/articles_turbo.csv"))
        duration = time.time() - start_time
        
        print(f"✓ Turbo scraped {len(result)} articles in {duration:.2f} seconds")
        print(f"✓ Output: output/articles_turbo.csv")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def main():
    """Run all examples."""
    import os
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    print("=" * 50)
    print("pipescraper Usage Examples")
    print("=" * 50)
    print()
    
    # Run examples
    # Note: Some examples are commented out to avoid actual web scraping
    # Uncomment to test with real websites
    
    # example_1_basic_pipeline()
    # example_2_filtered_pipeline()
    # example_3_limited_pipeline()
    # example_4_deduplication()
    # example_5_excel_output()
    # example_6_direct_url_extraction()
    # example_7_custom_filtering()
    # example_8_inspect_dataframe()
    # example_9_respecting_robots()
    example_10_error_handling()
    example_11_turbo_scraping()
    
    print("=" * 50)
    print("Examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
