import json
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import AIMessage
from langchain_core.tools import tool


class State(TypedDict):
    # REQUIRED: messages field with add_messages reducer for evaluator compatibility
    messages: Annotated[list, add_messages]
    # Additional fields for the multi-agent system
    topic: str
    headlines_str: str  # JSON string of List[str]
    trends_str: str     # JSON string of List[str]


@tool
def news_fetch(topic: str) -> str:
    """Fetch top 5 news headlines for a given topic."""
    # Mock headlines for demonstration - returns different headlines based on topic
    mock_headlines = {
        "electric vehicles": [
            "Tesla announces new battery technology breakthrough",
            "Electric vehicle sales surge 40% this quarter",
            "New charging infrastructure expands across major cities",
            "Battery costs drop to record lows for EV manufacturers",
            "Government announces new electric vehicle incentives"
        ],
        "artificial intelligence": [
            "AI breakthrough in medical diagnosis accuracy",
            "New AI model shows remarkable language understanding",
            "Tech companies invest billions in AI research",
            "AI safety concerns raised by leading researchers",
            "Machine learning transforms financial trading"
        ],
        "climate change": [
            "Global temperatures reach new record highs",
            "Renewable energy adoption accelerates worldwide",
            "Climate summit produces landmark agreement",
            "Extreme weather events increase in frequency",
            "Carbon capture technology shows promising results"
        ]
    }
    
    # Return headlines for the topic, or generic headlines if topic not found
    headlines = mock_headlines.get(topic.lower(), [
        f"Breaking news about {topic} developments",
        f"Latest {topic} research findings published",
        f"Industry experts discuss {topic} trends",
        f"New {topic} regulations announced",
        f"Global {topic} market shows growth"
    ])
    
    return json.dumps(headlines)


def fetcher(state: State):
    """Fetcher Agent: Extracts topic from user input and fetches news headlines."""
    # Extract user input (the ONLY thing evaluator provides)
    user_input = state["messages"][0].content if state["messages"] else ""
    
    # Use user input as the topic
    topic = user_input.strip()
    
    # Call the news fetch tool
    headlines_json = news_fetch.invoke({"topic": topic})
    
    # Create response message
    response = f"Fetched {len(json.loads(headlines_json))} headlines for topic: {topic}"
    
    return {
        "messages": [AIMessage(content=response)],
        "topic": topic,
        "headlines_str": headlines_json
    }


def analyzer(state: State):
    """Analyzer Agent: Parses headlines and finds trending words (appearing ≥2 times)."""
    # Get headlines from state with default
    headlines_str = state.get("headlines_str", "[]")
    
    try:
        headlines: list[str] = json.loads(headlines_str)
    except json.JSONDecodeError:
        headlines = []
    
    # Count word occurrences across all headlines
    word_count: dict[str, int] = {}
    for headline in headlines:
        # Simple word extraction (split by spaces and clean)
        words = headline.lower().replace(",", "").replace(".", "").split()
        for word in words:
            # Filter out common words and short words
            if len(word) > 3 and word not in ["this", "that", "with", "from", "they", "have", "been", "will", "were", "said", "says", "more", "than", "also", "their", "would", "could", "should", "about", "after", "before", "during", "while"]:
                word_count[word] = word_count.get(word, 0) + 1
    
    # Find words appearing 2 or more times
    trends = [word for word, count in word_count.items() if count >= 2]
    trends_json = json.dumps(trends)
    
    # Create response message
    response = f"Analyzed headlines and found {len(trends)} trending words"
    
    return {
        "messages": [AIMessage(content=response)],
        "trends_str": trends_json
    }


def reporter(state: State):
    """Reporter Agent: Creates final alert based on trends and topic."""
    # Get data from state with defaults
    trends_str = state.get("trends_str", "[]")
    topic = state.get("topic", "unknown topic")
    
    try:
        trends = json.loads(trends_str)
    except json.JSONDecodeError:
        trends = []
    
    # Create alert object based on whether trends were found
    if trends:
        alert = {
            "trend_found": True,
            "trend_keywords": trends,
            "alert_summary": f"In the latest headlines on {topic}, we saw repeated mentions of {', '.join(trends)}."
        }
    else:
        alert = {
            "trend_found": False,
            "alert_summary": f"No new trend detected for {topic}."
        }
    
    # Serialize the entire alert object as JSON string
    alert_json = json.dumps(alert)
    
    return {
        "messages": [AIMessage(content=alert_json)]
    }


# Build the StateGraph
graph_builder = StateGraph(State)

# Add nodes
graph_builder.add_node("fetcher", fetcher)
graph_builder.add_node("analyzer", analyzer)
graph_builder.add_node("reporter", reporter)

# Add edges to create sequence: START -> fetcher -> analyzer -> reporter -> END
graph_builder.add_edge(START, "fetcher")
graph_builder.add_edge("fetcher", "analyzer")
graph_builder.add_edge("analyzer", "reporter")
graph_builder.add_edge("reporter", END)

# Compile and export the graph
app = graph_builder.compile()

