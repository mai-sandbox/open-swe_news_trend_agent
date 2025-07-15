"""Multi-Agent News-Trend Alert System using LangGraph."""

import json
import re
from collections import Counter
from typing import Dict, List
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    """State schema for the news trend alert system."""
    topic: str
    headlines_str: str  # JSON string of List[str]
    trends_str: str     # JSON string of List[str]


def mock_news_fetch_tool(topic: str) -> List[str]:
    """Mock news-fetch tool that returns 5 sample headlines for any topic."""
    # Create sample headlines with some repeated words to enable trend detection
    sample_headlines = {
        "electric vehicles": [
            "Tesla announces new electric vehicle battery technology breakthrough",
            "Electric vehicle sales surge in Q4 with record-breaking numbers",
            "Major automakers invest billions in electric vehicle infrastructure",
            "New electric vehicle charging stations open across the country",
            "Government announces incentives for electric vehicle adoption"
        ],
        "artificial intelligence": [
            "AI breakthrough in medical diagnosis shows promising results",
            "Tech giants announce new AI safety regulations and guidelines",
            "AI-powered automation transforms manufacturing industry processes",
            "Researchers develop AI system for climate change prediction",
            "New AI chatbot technology revolutionizes customer service"
        ],
        "climate change": [
            "Climate change summit reaches historic agreement on emissions",
            "New study reveals accelerating climate change impacts globally",
            "Renewable energy solutions combat climate change effectively",
            "Scientists warn of irreversible climate change consequences",
            "Climate change adaptation strategies implemented worldwide"
        ]
    }
    
    # Return topic-specific headlines or generic ones
    if topic.lower() in sample_headlines:
        return sample_headlines[topic.lower()]
    else:
        # Generic headlines with repeated words for any topic
        return [
            f"Breaking news about {topic} developments announced today",
            f"Major {topic} breakthrough reported by leading experts",
            f"New {topic} research findings published in scientific journal",
            f"Industry leaders discuss {topic} future trends and implications",
            f"Government announces new {topic} policy and regulatory changes"
        ]


def fetcher(state: State) -> Dict[str, str]:
    """Fetcher agent node that gets headlines for the given topic."""
    topic = state["topic"]
    headlines = mock_news_fetch_tool(topic)
    headlines_json = json.dumps(headlines)
    return {"headlines_str": headlines_json}


def analyzer(state: State) -> Dict[str, str]:
    """Analyzer agent node that finds trending words appearing ≥2 times."""
    headlines_json = state["headlines_str"]
    headlines = json.loads(headlines_json)
    
    # Extract words from all headlines and count occurrences
    all_words = []
    for headline in headlines:
        # Convert to lowercase and extract words (alphanumeric only)
        words = re.findall(r'\b[a-zA-Z]+\b', headline.lower())
        all_words.extend(words)
    
    # Count word occurrences and find trends (words appearing ≥2 times)
    word_counts = Counter(all_words)
    trends = [word for word, count in word_counts.items() if count >= 2]
    
    # Filter out common stop words
    stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "about", "new", "announces"}
    trends = [word for word in trends if word not in stop_words]
    
    trends_json = json.dumps(trends)
    return {"trends_str": trends_json}


def reporter(state: State) -> Dict[str, str]:
    """Reporter agent node that creates the final alert summary."""
    trends_json = state["trends_str"]
    topic = state["topic"]
    trends = json.loads(trends_json)
    
    if trends:
        alert = {
            "trend_found": True,
            "trend_keywords": trends,
            "alert_summary": f"In the latest headlines on {topic}, we saw repeated mentions of {', '.join(trends)}."
        }
    else:
        alert = {
            "trend_found": False,
            "trend_keywords": [],
            "alert_summary": f"No new trend detected for {topic}."
        }
    
    return {"alert": json.dumps(alert)}


# Build the StateGraph
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("fetcher", fetcher)
graph_builder.add_node("analyzer", analyzer)
graph_builder.add_node("reporter", reporter)

# Add edges for sequential flow
graph_builder.add_edge(START, "fetcher")
graph_builder.add_edge("fetcher", "analyzer")
graph_builder.add_edge("analyzer", "reporter")
graph_builder.add_edge("reporter", END)

# Compile the graph
compiled_graph = graph_builder.compile()

