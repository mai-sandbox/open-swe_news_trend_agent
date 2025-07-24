import json
from collections import Counter
from typing import TypedDict, List

from langgraph.graph import StateGraph, START, END


# State Definition
class State(TypedDict):
    topic: str
    headlines_str: str
    trends_str: str
    report: str


# Mock News Fetcher Tool
def fetch_news(topic: str) -> List[str]:
    """
    Mock function to fetch news headlines.
    Returns a hardcoded list of headlines with overlapping keywords.
    """
    return [
        f"Big Tech's New AI Surpasses Human Performance in Tests",
        f"Stock Market Hits Record Highs Amidst AI Boom",
        f"New Regulations Proposed for AI Development and Deployment",
        f"AI in Healthcare: A Revolution in Diagnostics",
        f"The Future of Work: How AI is Changing the Job Market"
    ]


# Fetcher Agent Node
def fetcher(state: State) -> dict:
    """
    Fetches news headlines for the given topic and serializes them into a JSON string.
    """
    topic = state["topic"]
    headlines = fetch_news(topic)
    headlines_str = json.dumps(headlines)
    return {"headlines_str": headlines_str}


# Analyzer Agent Node
def analyzer(state: State) -> dict:
    """
    Analyzes headlines to find trending keywords.
    """
    headlines_str = state["headlines_str"]
    headlines = json.loads(headlines_str)

    all_words = [word.lower() for headline in headlines for word in headline.split()]
    word_counts = Counter(all_words)

    trends = [word for word, count in word_counts.items() if count >= 2]
    trends_str = json.dumps(trends)

    return {"trends_str": trends_str}


# Reporter Agent Node
def reporter(state: State) -> dict:
    """
    Generates a final report based on the identified trends.
    """
    trends_str = state["trends_str"]
    topic = state["topic"]
    trends = json.loads(trends_str)

    if trends:
        report_data = {
            "trend_found": True,
            "trend_keywords": trends,
            "alert_summary": f"In the latest headlines on {topic}, we saw repeated mentions of {', '.join(trends)}."
        }
    else:
        report_data = {
            "trend_found": False,
            "alert_summary": f"No new trend detected for {topic}."
        }

    report_str = json.dumps(report_data)
    return {"report": report_str}


# Graph Definition and Compilation
graph_builder = StateGraph(State)

graph_builder.add_node("fetcher", fetcher)
graph_builder.add_node("analyzer", analyzer)
graph_builder.add_node("reporter", reporter)

graph_builder.add_edge(START, "fetcher")
graph_builder.add_edge("fetcher", "analyzer")
graph_builder.add_edge("analyzer", "reporter")
graph_builder.add_edge("reporter", END)

compiled_graph = graph_builder.compile()


