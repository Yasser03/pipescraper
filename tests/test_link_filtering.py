import pytest
from pipescraper.core import LinkFetcher

def test_link_filtering_heuristics():
    """Test the improved link filtering heuristics with real-world examples."""
    fetcher = LinkFetcher()
    base_url = "https://www.chroniclelive.co.uk"
    
    # OK URLs
    ok_urls = [
        "https://www.chroniclelive.co.uk/news/north-east-news/join-chroniclelive-whatsapp-community-signup-26563249",
        "https://www.chroniclelive.co.uk/news/north-east-news/14-more-electric-buses-soon-33575655",
        "https://www.chroniclelive.co.uk/news/north-east-news/more-50m-funding-approved-transport-33575656",
        "https://www.chroniclelive.co.uk/news/north-east-news/untold-story-slice-luck-sparked-33539245",
        "https://www.chroniclelive.co.uk/news/north-east-news/sunderland-film-studio-can-still-33565151",
        "https://www.chroniclelive.co.uk/news/north-east-news/immature-newcastle-thug-who-attacked-33573425"
    ]
    
    # NOT OK URLs
    not_ok_urls = [
        "https://www.chroniclelive.co.uk/all-about/weather",
        "https://www.chroniclelive.co.uk/all-about/newcastle-crown-court",
        "https://www.chroniclelive.co.uk/whats-on/food-drink-news",
        "https://www.chroniclelive.co.uk/all-about/newcastle-upon-tyne",
        "https://www.chroniclelive.co.uk/all-about/nhs",
        "https://www.chroniclelive.co.uk/news/north-east-news/gallery/26-pictures-st-james-park-33572775",
        "https://www.chroniclelive.co.uk/whats-on/music-nightlife-news",
        "https://www.chroniclelive.co.uk/sport/other-sport",
        "https://www.chroniclelive.co.uk/all-about/things-to-do-newcastle",
        # New problematic hubs from user
        "https://www.chroniclelive.co.uk/news/uk-news",
        "https://www.chroniclelive.co.uk/news/cost-of-living",
        "https://www.chroniclelive.co.uk/news/property-news",
        "https://www.chroniclelive.co.uk/news/health"
    ]
    
    for url in ok_urls:
        assert fetcher._is_article_link(url, base_url), f"Should be OK: {url}"
        
    for url in not_ok_urls:
        assert not fetcher._is_article_link(url, base_url), f"Should NOT be OK: {url}"
