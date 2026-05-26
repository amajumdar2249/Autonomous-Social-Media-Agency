# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock

from agency import scraper

def test_fetch_all_news_success(mocker):
    # Mock feedparser.parse
    mock_feed = MagicMock()
    mock_entry_1 = {
        "title": "AI is changing the world",
        "summary": "<p>A quick summary of the article about AI.</p>",
        "link": "https://example.com/ai-changing-world"
    }
    mock_entry_2 = {
        "title": "Startup building new LLMs",
        "summary": "This is another description.",
        "link": "https://example.com/startup-llms"
    }
    mock_feed.entries = [mock_entry_1, mock_entry_2]
    mocker.patch("feedparser.parse", return_value=mock_feed)
    
    # Mock is_duplicate to always return False
    mocker.patch("agency.scraper.is_duplicate", return_value=False)
    
    news = scraper.fetch_all_news(max_per_feed=2)
    
    # Expect 2 unique news entries (in-memory deduplication filters out duplicates on subsequent feeds)
    assert len(news) == 2
    assert news[0]["title"] == "AI is changing the world"
    assert "p>" not in news[0]["summary"]  # HTML cleaned
    assert news[0]["link"] == "https://example.com/ai-changing-world"

def test_fetch_all_news_with_duplicates(mocker):
    mock_feed = MagicMock()
    mock_entry_1 = {"title": "Duplicate title", "summary": "desc", "link": "link"}
    mock_feed.entries = [mock_entry_1]
    mocker.patch("feedparser.parse", return_value=mock_feed)
    
    # First time call is_duplicate returns False, second time returns True
    mock_is_dup = MagicMock(side_effect=[False, True, True, True])
    mocker.patch("agency.scraper.is_duplicate", mock_is_dup)
    
    news = scraper.fetch_all_news(max_per_feed=1)
    # Only 1 unique topic should be returned, others filtered by deduplication
    assert len(news) == 1
    assert news[0]["title"] == "Duplicate title"
