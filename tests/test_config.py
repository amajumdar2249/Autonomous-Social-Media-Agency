# -*- coding: utf-8 -*-
from agency.config import (
    MAX_TOKENS, DEFAULT_TEMPERATURE, MIN_VIRALITY_SCORE,
    NICHE_KEYWORDS, RSS_FEEDS, POST_TEMPLATES, VOICE
)

def test_config_constants():
    assert MAX_TOKENS == 800
    assert DEFAULT_TEMPERATURE == 0.85
    assert MIN_VIRALITY_SCORE == 7.5

def test_config_lists():
    assert len(NICHE_KEYWORDS) > 0
    assert "artificial intelligence" in NICHE_KEYWORDS
    assert len(RSS_FEEDS) == 4
    assert all(url.startswith("http") for url in RSS_FEEDS)

def test_post_templates():
    assert len(POST_TEMPLATES) == 4
    for name, prompt in POST_TEMPLATES:
        assert name in ["INSIDER TRUTH", "STORY THAT TEACHES", "CONTRARIAN TAKE", "WITTY OBSERVER"]
        assert "{{VOICE}}" in prompt
        assert "{{TOPIC}}" in prompt
        assert "{{CONTEXT}}" in prompt

def test_voice_dna():
    assert len(VOICE) > 100
    assert "founder's exact voice" in VOICE
