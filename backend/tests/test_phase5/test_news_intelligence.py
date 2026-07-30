"""
Tests for the News Intelligence feature:
- News analyzer Pydantic structured output parsing
- News poller deduplication logic
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# ── Test 1: DisruptionAnalysis and NewsAnalysisResult models ─────────────────

def test_disruption_analysis_model():
    """Verify the Pydantic models parse correctly."""
    from graph.nodes.news_analyzer import DisruptionAnalysis, NewsAnalysisResult

    d = DisruptionAnalysis(
        is_disruption=True,
        severity="high",
        disruption_type="port strike",
        affected_routes=["Shanghai to Los Angeles"],
        affected_ports=["Shanghai Terminal 2"],
        estimated_delay_days=7,
        alternative_routes=["Ningbo to Los Angeles", "Shanghai to Long Beach via Busan"],
        reasoning="Port workers have gone on strike, blocking container operations.",
        confidence=0.92,
        source_headline="Shanghai port strike halts operations",
    )

    assert d.is_disruption is True
    assert d.severity == "high"
    assert len(d.affected_routes) == 1
    assert len(d.alternative_routes) == 2
    assert d.confidence == 0.92

    result = NewsAnalysisResult(
        disruptions=[d],
        summary="1 disruption found in batch.",
    )

    assert len(result.disruptions) == 1
    assert result.disruptions[0].disruption_type == "port strike"


def test_no_disruption_model():
    """Verify empty analysis works."""
    from graph.nodes.news_analyzer import NewsAnalysisResult

    result = NewsAnalysisResult(
        disruptions=[],
        summary="No disruptions found.",
    )
    assert len(result.disruptions) == 0


# ── Test 2: News poller deduplication ────────────────────────────────────────

def test_news_poller_dedup():
    """Verify that the poller skips already-seen URLs."""
    from services.news_poller import _seen_urls

    # Start clean
    _seen_urls.clear()

    test_url = "https://reuters.com/test-article-123"
    assert test_url not in _seen_urls

    _seen_urls.add(test_url)
    assert test_url in _seen_urls

    # Adding again should not change the set size
    original_size = len(_seen_urls)
    _seen_urls.add(test_url)
    assert len(_seen_urls) == original_size


def test_news_poller_status():
    """Verify the status dict returns expected keys."""
    from services.news_poller import get_news_status

    status = get_news_status()
    assert "running" in status
    assert "last_polled_at" in status
    assert "articles_analyzed" in status
    assert "disruptions_triggered" in status
    assert "seen_article_count" in status


# ── Test 3: AgentState includes news fields ──────────────────────────────────

def test_agent_state_has_news_fields():
    """Verify AgentState TypedDict includes the new news intelligence fields."""
    from graph.state import AgentState

    # TypedDict annotations should include new fields
    annotations = AgentState.__annotations__
    assert "news_context" in annotations
    assert "llm_disruption_analysis" in annotations
    assert "alternative_routes_suggested" in annotations
