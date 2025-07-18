import json
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    topic: str
    headlines_str: str  # JSON string of List[str]
    trends_str: str     # JSON string of List[str]


def fetcher_agent(state: State) -> dict:
    """
    Fetcher Agent: Takes state["topic"] and creates mock news headlines.
    Returns the headlines list serialized as a JSON string in state["headlines_str"].
    """
    topic = state["topic"]
    
    # Create mock headlines for the given topic
    mock_headlines = [
        f"Breaking: Major {topic} development announced by industry leaders",
        f"New {topic} technology promises revolutionary changes ahead",
        f"Market analysis shows {topic} sector experiencing significant growth",
        f"Experts predict {topic} will transform the industry landscape",
        f"Latest {topic} innovations capture global attention and investment"
    ]
    
    # Serialize headlines as JSON string
    headlines_json = json.dumps(mock_headlines)
    
    return {"headlines_str": headlines_json}


def analyzer_agent(state: State) -> dict:
    """
    Analyzer Agent: Parses state["headlines_str"] and finds words appearing ≥2 times.
    Returns the trends list serialized as a JSON string in state["trends_str"].
    """
    # Parse headlines from JSON string
    headlines = json.loads(state["headlines_str"])
    
    # Word frequency analysis
    word_count = {}
    for headline in headlines:
        # Split into words and normalize (lowercase, remove punctuation)
        words = headline.lower().replace(",", "").replace(":", "").replace(".", "").split()
        for word in words:
            # Skip common words and short words
            if len(word) > 2 and word not in ["the", "and", "for", "are", "will", "new", "major"]:
                word_count[word] = word_count.get(word, 0) + 1
    
    # Find words appearing ≥2 times
    trends = [word for word, count in word_count.items() if count >= 2]
    
    # Serialize trends as JSON string
    trends_json = json.dumps(trends)
    
    return {"trends_str": trends_json}


def reporter_agent(state: State) -> dict:
    """
    Reporter Agent: Creates alert object based on trends and topic.
    Returns the complete alert object serialized as a JSON string.
    """
    topic = state["topic"]
    trends = json.loads(state["trends_str"])
    
    if trends:
        # Create alert object when trends exist
        alert_object = {
            "trend_found": True,
            "trend_keywords": trends,
            "alert_summary": f"In the latest headlines on {topic}, we saw repeated mentions of {', '.join(trends)}."
        }
    else:
        # Create alert object when no trends found
        alert_object = {
            "trend_found": False,
            "alert_summary": f"No new trend detected for {topic}."
        }
    
    # Return the complete alert object as JSON string
    return json.dumps(alert_object)


# Build the StateGraph
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("fetcher", fetcher_agent)
graph_builder.add_node("analyzer", analyzer_agent)
graph_builder.add_node("reporter", reporter_agent)

# Add edges to create sequential flow
graph_builder.add_edge(START, "fetcher")
graph_builder.add_edge("fetcher", "analyzer")
graph_builder.add_edge("analyzer", "reporter")
graph_builder.add_edge("reporter", END)

# Compile the graph
graph = graph_builder.compile()

# Export the compiled graph as required
compiled_graph = graph


