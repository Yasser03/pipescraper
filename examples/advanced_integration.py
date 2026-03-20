"""
Advanced usage examples for pipescraper with PipeFrame and PipePlotly integration.

This script demonstrates how to use pipescraper with PipeFrame for data manipulation
and PipePlotly for visualization, creating complete end-to-end pipelines.

Note: These examples require pipeframe and pipeplotly to be installed:
    pip install pipescraper[all]
    # or
    pip install pipescraper[pipeframe]
    pip install pipescraper[pipeplotly]
"""

from pipescraper import (
    FetchLinks,
    ExtractArticles,
    ToPipeFrame,
    SaveAs,
    PIPEFRAME_AVAILABLE,
    PIPEPLOTLY_AVAILABLE,
)


def example_1_pipeframe_basic():
    """
    Example 1: Basic PipeFrame integration.
    
    Demonstrates using PipeFrame verbs (select, filter, arrange) in a
    pipescraper pipeline.
    """
    if not PIPEFRAME_AVAILABLE:
        print("⚠️  PipeFrame not installed. Install with: pip install pipeframe")
        return
    
    from pipeframe import select, filter, arrange
    
    print("Example 1: Basic PipeFrame Integration")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        result = (base_url
                  >> FetchLinks(max_links=10)
                  >> ExtractArticles()
                  >> ToPipeFrame(include_text=False)
                  >> select('title', 'author', 'date_published', 'source')
                  >> filter(lambda df: df['author'].notna())
                  >> arrange('date_published', ascending=False))
        
        print(f"✓ Processed {len(result)} articles with PipeFrame")
        print(f"\nFirst few rows:")
        print(result.head())
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_2_pipeframe_mutate():
    """
    Example 2: Using PipeFrame's mutate for data transformation.
    
    Demonstrates creating new columns based on existing data.
    """
    if not PIPEFRAME_AVAILABLE:
        print("⚠️  PipeFrame not installed. Install with: pip install pipeframe")
        return
    
    from pipeframe import select, mutate, arrange
    
    print("Example 2: PipeFrame Mutate")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        result = (base_url
                  >> FetchLinks(max_links=10)
                  >> ExtractArticles()
                  >> ToPipeFrame()
                  >> mutate(
                      text_length=lambda df: df['text'].str.len(),
                      has_author=lambda df: df['author'].notna(),
                      title_length=lambda df: df['title'].str.len()
                  )
                  >> select('title', 'text_length', 'has_author', 'date_published')
                  >> arrange('text_length', ascending=False))
        
        print(f"✓ Created new columns with mutate")
        print(f"\nResults:")
        print(result.head())
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_3_pipeframe_group_summarize():
    """
    Example 3: Grouping and summarizing with PipeFrame.
    
    Demonstrates aggregation operations.
    """
    if not PIPEFRAME_AVAILABLE:
        print("⚠️  PipeFrame not installed. Install with: pip install pipeframe")
        return
    
    from pipeframe import group_by, summarize, arrange, mutate
    
    print("Example 3: PipeFrame Group and Summarize")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        result = (base_url
                  >> FetchLinks(max_links=20)
                  >> ExtractArticles()
                  >> ToPipeFrame()
                  >> mutate(text_length=lambda df: df['text'].str.len())
                  >> group_by('source')
                  >> summarize(
                      article_count=('title', 'count'),
                      avg_text_length=('text_length', 'mean'),
                      total_articles=('title', 'size')
                  )
                  >> arrange('article_count', ascending=False))
        
        print(f"✓ Grouped and summarized by source")
        print(f"\nResults:")
        print(result)
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_4_pipeplotly_bar_chart():
    """
    Example 4: Creating visualizations with PipePlotly.
    
    Demonstrates creating a bar chart of articles by source.
    """
    if not PIPEFRAME_AVAILABLE or not PIPEPLOTLY_AVAILABLE:
        print("⚠️  PipeFrame or PipePlotly not installed.")
        print("Install with: pip install pipescraper[all]")
        return
    
    from pipeframe import mutate
    from pipeplotly import ggplot, aes, geom_bar, labs, theme_minimal
    
    print("Example 4: PipePlotly Bar Chart")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        fig = (base_url
               >> FetchLinks(max_links=15)
               >> ExtractArticles()
               >> ToPipeFrame(include_text=False)
               >> ggplot(aes(x='source'))
               >> geom_bar()
               >> labs(
                   title='Articles by Source',
                   x='Source',
                   y='Number of Articles'
               )
               >> theme_minimal())
        
        print(f"✓ Created bar chart")
        print(f"✓ Figure object created (use .show() to display)")
        # fig.show()  # Uncomment to display
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_5_pipeplotly_scatter():
    """
    Example 5: Scatter plot with PipePlotly.
    
    Demonstrates creating a scatter plot of article metrics.
    """
    if not PIPEFRAME_AVAILABLE or not PIPEPLOTLY_AVAILABLE:
        print("⚠️  PipeFrame or PipePlotly not installed.")
        print("Install with: pip install pipescraper[all]")
        return
    
    from pipeframe import mutate, filter
    from pipeplotly import ggplot, aes, geom_point, labs, theme_minimal
    
    print("Example 5: PipePlotly Scatter Plot")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        fig = (base_url
               >> FetchLinks(max_links=20)
               >> ExtractArticles()
               >> ToPipeFrame()
               >> mutate(
                   text_length=lambda df: df['text'].str.len(),
                   title_length=lambda df: df['title'].str.len()
               )
               >> filter(lambda df: df['text_length'] > 0)
               >> ggplot(aes(x='title_length', y='text_length', color='source'))
               >> geom_point()
               >> labs(
                   title='Article Title Length vs Text Length',
                   x='Title Length (characters)',
                   y='Text Length (characters)'
               )
               >> theme_minimal())
        
        print(f"✓ Created scatter plot")
        print(f"✓ Figure object created (use .show() to display)")
        # fig.show()  # Uncomment to display
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_6_pipeplotly_timeline():
    """
    Example 6: Timeline visualization with PipePlotly.
    
    Demonstrates creating a timeline of article publications.
    """
    if not PIPEFRAME_AVAILABLE or not PIPEPLOTLY_AVAILABLE:
        print("⚠️  PipeFrame or PipePlotly not installed.")
        print("Install with: pip install pipescraper[all]")
        return
    
    from pipeframe import filter, mutate
    from pipeplotly import ggplot, aes, geom_line, labs, theme_minimal
    import pandas as pd
    
    print("Example 6: PipePlotly Timeline")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        fig = (base_url
               >> FetchLinks(max_links=20)
               >> ExtractArticles()
               >> ToPipeFrame(include_text=False)
               >> filter(lambda df: df['date_published'].notna())
               >> mutate(date=lambda df: pd.to_datetime(df['date_published']))
               >> ggplot(aes(x='date'))
               >> geom_line(stat='count')
               >> labs(
                   title='Articles Published Over Time',
                   x='Publication Date',
                   y='Number of Articles'
               )
               >> theme_minimal())
        
        print(f"✓ Created timeline visualization")
        print(f"✓ Figure object created (use .show() to display)")
        # fig.show()  # Uncomment to display
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_7_complete_pipeline():
    """
    Example 7: Complete end-to-end pipeline.
    
    Demonstrates a full pipeline: scrape → transform → visualize → save.
    """
    if not PIPEFRAME_AVAILABLE or not PIPEPLOTLY_AVAILABLE:
        print("⚠️  PipeFrame or PipePlotly not installed.")
        print("Install with: pip install pipescraper[all]")
        return
    
    from pipeframe import select, filter, mutate, arrange
    from pipeplotly import create_articles_by_source_chart
    import os
    
    print("Example 7: Complete End-to-End Pipeline")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    os.makedirs("output", exist_ok=True)
    
    try:
        # Data pipeline
        data = (base_url
                >> FetchLinks(max_links=20)
                >> ExtractArticles(delay=2.0)
                >> ToPipeFrame()
                >> mutate(
                    text_length=lambda df: df['text'].str.len(),
                    has_author=lambda df: df['author'].notna()
                )
                >> filter(lambda df: df['text_length'] > 500)
                >> select('title', 'author', 'source', 'date_published', 
                       'text_length', 'has_author')
                >> arrange('date_published', ascending=False))
        
        # Save processed data
        data >> SaveAs("output/processed_articles.csv")
        print(f"✓ Saved processed data to output/processed_articles.csv")
        
        # Create visualization
        fig = create_articles_by_source_chart(
            data,
            title='Distribution of Articles by Source'
        )
        print(f"✓ Created visualization")
        # fig.show()  # Uncomment to display
        
        print(f"\nProcessed {len(data)} articles")
        print(f"Average text length: {data['text_length'].mean():.0f} characters")
        print(f"Articles with authors: {data['has_author'].sum()}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def example_8_helper_visualizations():
    """
    Example 8: Using built-in visualization helpers.
    
    Demonstrates pipescraper's helper functions for common visualizations.
    """
    if not PIPEFRAME_AVAILABLE or not PIPEPLOTLY_AVAILABLE:
        print("⚠️  PipeFrame or PipePlotly not installed.")
        print("Install with: pip install pipescraper[all]")
        return
    
    from pipescraper import (
        create_articles_by_source_chart,
        create_text_length_distribution,
        create_articles_by_language,
    )
    from pipeframe import mutate
    
    print("Example 8: Helper Visualization Functions")
    print("-" * 50)
    
    base_url = "https://news.ycombinator.com"
    
    try:
        # Get data
        data = (base_url
                >> FetchLinks(max_links=15)
                >> ExtractArticles()
                >> ToPipeFrame())
        
        # Create multiple visualizations
        fig1 = create_articles_by_source_chart(data)
        print(f"✓ Created source distribution chart")
        
        fig2 = create_text_length_distribution(data)
        print(f"✓ Created text length distribution")
        
        fig3 = create_articles_by_language(data)
        print(f"✓ Created language distribution chart")
        
        print(f"\nAll visualizations created successfully!")
        # fig1.show(), fig2.show(), fig3.show()  # Uncomment to display
        
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print()


def main():
    """Run all advanced examples."""
    import os
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    print("=" * 50)
    print("pipescraper Advanced Examples")
    print("PipeFrame & PipePlotly Integration")
    print("=" * 50)
    print()
    
    # Check availability
    if PIPEFRAME_AVAILABLE:
        print("✓ PipeFrame is installed and available")
    else:
        print("✗ PipeFrame not installed (pip install pipeframe)")
    
    if PIPEPLOTLY_AVAILABLE:
        print("✓ PipePlotly is installed and available")
    else:
        print("✗ PipePlotly not installed (pip install pipeplotly)")
    
    print()
    print("To install both: pip install pipescraper[all]")
    print()
    print("-" * 50)
    print()
    
    # Run examples (commented out to avoid actual scraping)
    # Uncomment to test
    
    # example_1_pipeframe_basic()
    # example_2_pipeframe_mutate()
    # example_3_pipeframe_group_summarize()
    # example_4_pipeplotly_bar_chart()
    # example_5_pipeplotly_scatter()
    # example_6_pipeplotly_timeline()
    # example_7_complete_pipeline()
    # example_8_helper_visualizations()
    
    print("=" * 50)
    print("Examples completed!")
    print("=" * 50)


if __name__ == "__main__":
    main()
