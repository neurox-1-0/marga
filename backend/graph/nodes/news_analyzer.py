"""
backend/graph/nodes/news_analyzer.py

Uses Gemini 2.5 Pro to reason over a batch of news headlines and determine
whether they represent real supply chain / logistics disruptions.

This is called by the news_poller service, NOT as a LangGraph node.
It returns structured analysis that the poller uses to decide whether
to trigger the agent.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import logging

logger = logging.getLogger(__name__)

# ── Structured output schema ────────────────────────────────────────────────

class DisruptionAnalysis(BaseModel):
    """Structured LLM output for a single identified disruption."""
    is_disruption: bool = Field(description="Whether this news constitutes a real logistics/shipping disruption.")
    severity: str = Field(description="Severity level: 'low', 'medium', 'high', or 'critical'.")
    disruption_type: str = Field(description="Type of disruption, e.g. 'port strike', 'typhoon', 'canal blockage', 'customs delay'.")
    affected_routes: List[str] = Field(default_factory=list, description="Affected shipping routes, e.g. ['Shanghai to Los Angeles'].")
    affected_ports: List[str] = Field(default_factory=list, description="Affected ports or terminals.")
    estimated_delay_days: int = Field(default=0, description="Estimated delay in days caused by this disruption.")
    alternative_routes: List[str] = Field(default_factory=list, description="Suggested alternative routes or ports to avoid the disruption.")
    reasoning: str = Field(description="Chain-of-thought explanation of your analysis.")
    confidence: float = Field(description="Confidence score between 0.0 and 1.0.")
    source_headline: str = Field(default="", description="The headline that triggered this analysis.")


class NewsAnalysisResult(BaseModel):
    """Top-level result wrapping zero or more identified disruptions."""
    disruptions: List[DisruptionAnalysis] = Field(default_factory=list)
    summary: str = Field(description="Brief summary of the overall news batch analysis.")


# ── LLM setup (lazy to allow import without API key in tests) ────────────────

_analysis_llm = None
_structured_llm = None

def _get_structured_llm():
    global _analysis_llm, _structured_llm
    if _structured_llm is None:
        _analysis_llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro", temperature=0.1)
        _structured_llm = _analysis_llm.with_structured_output(NewsAnalysisResult)
    return _structured_llm


# ── Core analysis function ──────────────────────────────────────────────────

async def analyze_news_batch(articles: List[dict]) -> NewsAnalysisResult:
    """
    Send a batch of news articles to Gemini 2.5 Pro and get structured
    disruption analysis.

    Each article dict should have:
        - title: str
        - description: str (snippet)
        - url: str
        - publishedAt: str
        - source: str
    """
    if not articles:
        return NewsAnalysisResult(disruptions=[], summary="No articles to analyze.")

    # Build the prompt with all articles
    articles_text = ""
    for i, article in enumerate(articles, 1):
        articles_text += (
            f"\n--- Article {i} ---\n"
            f"Headline: {article.get('title', 'N/A')}\n"
            f"Source: {article.get('source', 'N/A')}\n"
            f"Published: {article.get('publishedAt', 'N/A')}\n"
            f"Snippet: {article.get('description', 'N/A')}\n"
        )

    prompt = f"""You are a supply chain intelligence analyst for a global logistics company.

Your task: Analyze the following batch of news articles and determine which ones
represent REAL disruptions to global shipping, logistics, or supply chains.

For each disruption you identify, provide:
1. The severity (low/medium/high/critical)
2. Which shipping routes are affected (use format "Origin to Destination", e.g. "Shanghai to Los Angeles")
3. Which ports or terminals are affected
4. Estimated delay in days
5. Alternative routes or ports that could be used to avoid the disruption
6. Your detailed reasoning

IMPORTANT GUIDELINES:
- Only flag articles about ACTUAL disruptions (strikes, storms, blockages, congestion, sanctions, accidents).
- Ignore general industry news, opinion pieces, or market analysis that don't describe a specific disruption event.
- For alternative routes, think practically about real shipping lanes and logistics hubs.
- Be specific about affected routes — map the disruption to actual trade lanes.

NEWS ARTICLES:
{articles_text}

Analyze these articles and identify any supply chain disruptions."""

    try:
        result: NewsAnalysisResult = await _get_structured_llm().ainvoke([HumanMessage(content=prompt)])
        logger.info(
            f"[News Analyzer] Analyzed {len(articles)} articles. "
            f"Found {len(result.disruptions)} disruptions."
        )
        return result
    except Exception as e:
        logger.error(f"[News Analyzer] Gemini analysis failed: {e}")
        return NewsAnalysisResult(
            disruptions=[],
            summary=f"Analysis failed: {str(e)}"
        )
