"""
backend/services/news_poller.py

Background NewsAPI polling service.

Polls NewsAPI.org every 15 minutes for logistics/shipping disruption keywords.
When new articles are found, sends them to Gemini 2.5 Pro for analysis.
If the LLM identifies a real disruption, triggers the LangGraph agent.

Runs as an asyncio background task started from main.py on startup.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Optional
import httpx

logger = logging.getLogger(__name__)

# ── Configuration ───────────────────────────────────────────────────────────

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")
NEWS_API_BASE = "https://newsapi.org/v2"
POLL_INTERVAL_SECONDS = 900  # 15 minutes (free tier: 100 req/day → ~96 polls/day)

# Keywords that signal potential logistics disruptions
SEARCH_QUERIES = [
    "port strike shipping",
    "canal blocked shipping",
    "supply chain disruption",
    "freight delay logistics",
    "typhoon shipping route",
    "shipping port congestion",
]

# ── In-memory deduplication ─────────────────────────────────────────────────

_seen_urls: set[str] = set()
_poller_status: dict = {
    "running": False,
    "last_polled_at": None,
    "last_disruption_found": None,
    "articles_analyzed": 0,
    "disruptions_triggered": 0,
    "errors": 0,
}


# ── NewsAPI fetching ────────────────────────────────────────────────────────

async def _fetch_news(client: httpx.AsyncClient, query: str) -> list[dict]:
    """Fetch articles from NewsAPI for a given query."""
    if not NEWS_API_KEY:
        logger.warning("[News Poller] NEWS_API_KEY not set. Skipping fetch.")
        return []

    try:
        resp = await client.get(
            f"{NEWS_API_BASE}/everything",
            params={
                "q": query,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 5,
                "apiKey": NEWS_API_KEY,
            },
            timeout=15.0,
        )
        resp.raise_for_status()
        data = resp.json()
        articles = data.get("articles", [])

        # Normalize to our internal format
        normalized = []
        for a in articles:
            url = a.get("url", "")
            if url in _seen_urls:
                continue
            _seen_urls.add(url)
            normalized.append({
                "title": a.get("title", ""),
                "description": a.get("description", ""),
                "url": url,
                "publishedAt": a.get("publishedAt", ""),
                "source": a.get("source", {}).get("name", "Unknown"),
            })
        return normalized

    except Exception as e:
        logger.warning(f"[News Poller] Failed to fetch news for '{query}': {e}")
        return []


# ── Trigger agent from disruption analysis ──────────────────────────────────

async def _trigger_agent_from_news(disruption, articles_context: str):
    """Kick off the LangGraph agent for a news-detected disruption."""
    from ..graph.builder import graph
    from ..db import crud
    from ..models.database import AsyncSessionLocal
    from ..websockets.manager import broadcast_agent_thought

    event_id = f"NEWS-{str(uuid.uuid4())[:8].upper()}"
    thread_id = f"{event_id}-{str(uuid.uuid4())[:8]}"
    config = {"configurable": {"thread_id": thread_id}}

    # Persist thread mapping
    try:
        async with AsyncSessionLocal() as db:
            await crud.save_thread(db, event_id, thread_id)
    except Exception as e:
        logger.warning(f"[News Poller] Could not persist thread: {e}")

    # Build the route string from the analysis
    route = disruption.affected_routes[0] if disruption.affected_routes else "Unknown Route"

    initial_state = {
        "event_id": event_id,
        "raw_event": {
            "source": f"NEWS ({disruption.source_headline[:60]}...)" if len(disruption.source_headline) > 60 else f"NEWS ({disruption.source_headline})",
            "vessel_id": "NEWS-AUTO",
            "route": route,
            "description": disruption.reasoning,
            "event_type": disruption.disruption_type,
            "severity": disruption.severity,
        },
        "news_context": articles_context,
        "llm_disruption_analysis": {
            "severity": disruption.severity,
            "disruption_type": disruption.disruption_type,
            "affected_routes": disruption.affected_routes,
            "affected_ports": disruption.affected_ports,
            "estimated_delay_days": disruption.estimated_delay_days,
            "alternative_routes": disruption.alternative_routes,
            "reasoning": disruption.reasoning,
            "confidence": disruption.confidence,
        },
        "alternative_routes_suggested": disruption.alternative_routes,
    }

    # Broadcast that we detected a disruption from news
    await broadcast_agent_thought(
        node="news_analyzer",
        thought=(
            f"🗞️ Disruption detected from news: {disruption.disruption_type} "
            f"({disruption.severity} severity). "
            f"Affected routes: {', '.join(disruption.affected_routes)}. "
            f"LLM suggests alternatives: {', '.join(disruption.alternative_routes) or 'None yet'}. "
            f"Confidence: {disruption.confidence:.0%}"
        ),
        confidence_score=disruption.confidence,
        tool_calls=[{"tool_name": "news_analysis", "rationale": disruption.reasoning[:120]}],
    )

    logger.info(f"[News Poller] Triggering agent for {event_id}: {disruption.disruption_type} on {route}")
    _poller_status["last_disruption_found"] = datetime.now(timezone.utc).isoformat()
    _poller_status["disruptions_triggered"] += 1

    try:
        await graph.ainvoke(initial_state, config=config)
        logger.info(f"[News Poller] Agent completed for {event_id}")
    except Exception as e:
        logger.error(f"[News Poller] Agent error for {event_id}: {e}")


# ── Core poll cycle ─────────────────────────────────────────────────────────

async def _poll_once():
    """Single poll cycle: fetch news → analyze with Gemini → trigger if needed."""
    from ..graph.nodes.news_analyzer import analyze_news_batch

    all_articles = []
    async with httpx.AsyncClient() as client:
        for query in SEARCH_QUERIES:
            articles = await _fetch_news(client, query)
            all_articles.extend(articles)

    if not all_articles:
        return

    # Cap at 10 articles per analysis batch to stay within context limits
    batch = all_articles[:10]
    _poller_status["articles_analyzed"] += len(batch)

    logger.info(f"[News Poller] Analyzing {len(batch)} new articles with Gemini 2.5 Pro...")

    result = await analyze_news_batch(batch)

    # Build a context string from the articles for the agent state
    articles_context = "\n\n".join(
        f"[{a['source']}] {a['title']}\n{a['description']}"
        for a in batch
    )

    for disruption in result.disruptions:
        if disruption.is_disruption and disruption.confidence >= 0.6:
            asyncio.create_task(
                _trigger_agent_from_news(disruption, articles_context)
            )


# ── Background polling loop ────────────────────────────────────────────────

async def run_news_poller():
    """Main polling loop. Started as a background task from main.py."""
    if not NEWS_API_KEY:
        logger.warning(
            "[News Poller] NEWS_API_KEY not set. News polling is disabled. "
            "Set it in .env to enable. You can still use /events/news/simulate."
        )
        _poller_status["running"] = False
        return

    logger.info(f"[News Poller] Starting. Will poll every {POLL_INTERVAL_SECONDS}s.")
    _poller_status["running"] = True

    while True:
        try:
            _poller_status["last_polled_at"] = datetime.now(timezone.utc).isoformat()
            await _poll_once()
        except Exception as e:
            logger.error(f"[News Poller] Unexpected error: {e}")
            _poller_status["errors"] += 1

        await asyncio.sleep(POLL_INTERVAL_SECONDS)


def get_news_status() -> dict:
    """Return current poller status for the /events/news/status endpoint."""
    return {**_poller_status, "seen_article_count": len(_seen_urls)}


# ── Manual simulation (for demos without an API key) ────────────────────────

async def simulate_news_article(
    headline: str,
    description: str,
    source: str = "Reuters",
):
    """
    Manually inject a fake news article into the analysis pipeline.
    Used by the /events/news/simulate endpoint for demos.
    """
    from ..graph.nodes.news_analyzer import analyze_news_batch
    from ..websockets.manager import broadcast_agent_thought

    await broadcast_agent_thought(
        node="news_poller",
        thought=f"📰 Simulated news article received: \"{headline}\"",
        confidence_score=1.0,
    )

    fake_article = {
        "title": headline,
        "description": description,
        "url": f"https://simulated.news/{uuid.uuid4()}",
        "publishedAt": datetime.now(timezone.utc).isoformat(),
        "source": source,
    }

    result = await analyze_news_batch([fake_article])

    articles_context = f"[{source}] {headline}\n{description}"

    triggered = []
    for disruption in result.disruptions:
        if disruption.is_disruption and disruption.confidence >= 0.4:  # Lower threshold for simulations
            asyncio.create_task(_trigger_agent_from_news(disruption, articles_context))
            triggered.append({
                "type": disruption.disruption_type,
                "severity": disruption.severity,
                "routes": disruption.affected_routes,
                "alternatives": disruption.alternative_routes,
                "confidence": disruption.confidence,
            })

    return {
        "analyzed": True,
        "disruptions_found": len(result.disruptions),
        "disruptions_triggered": len(triggered),
        "details": triggered,
        "summary": result.summary,
    }
