# -*- coding: utf-8 -*-
import pytest
from unittest.mock import MagicMock

from agency import generator

def test_is_relevant_true(mocker):
    mocker.patch("agency.generator.call_llm", return_value="YES")
    assert generator.is_relevant("title", "summary") is True

def test_is_relevant_false(mocker):
    mocker.patch("agency.generator.call_llm", return_value="NO")
    assert generator.is_relevant("title", "summary") is False

def test_rate_topic(mocker):
    mocker.patch("agency.generator.call_llm", return_value="8.5 out of 10")
    score = generator.rate_topic("title", "summary")
    assert score == 8.5

def test_filter_and_score(mocker):
    # Mock is_relevant
    mocker.patch("agency.generator.is_relevant", side_effect=[True, False])
    # Mock rate_topic
    mocker.patch("agency.generator.rate_topic", return_value=8.0)
    
    topics = [
        {"title": "Topic 1", "summary": "sum 1", "link": "link 1"},
        {"title": "Topic 2", "summary": "sum 2", "link": "link 2"}
    ]
    
    qualified = generator.filter_and_score(topics, min_score=7.5)
    
    assert len(qualified) == 1
    assert qualified[0]["title"] == "Topic 1"
    assert qualified[0]["score"] == 8.0

def test_generate_posts(mocker):
    mocker.patch("agency.generator.call_llm", return_value="This is a generated post content.")
    
    posts = generator.generate_posts("Topic Title", "Topic Summary")
    
    assert len(posts) == 4
    assert posts[0]["post_number"] == 1
    assert posts[0]["angle"] == "INSIDER TRUTH"
    assert posts[0]["text"] == "This is a generated post content."
