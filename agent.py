import json
from typing import Annotated, TypedDict
from langchain_core.tools import tool
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    # REQUIRED: messages field with add_messages reducer for evaluator
    messages: Annotated[list, add_messages]
    # Additional fields for multi-agent workflow
    topic: str
    headlines_str: str  # JSON string of List[str]
    trends_str: str     # JSON string of List[str]


@tool
def news_fetch_tool(topic: str) -> str:
    """Simulate fetching top 5 headlines for a given topic."""
    # Simulate news headlines for different topics
    simulated_headlines = {
        "electric vehicles": [
            "Tesla announces new battery technology breakthrough",
            "Electric vehicle sales surge 40% in Q4",
            "New charging infrastructure expands across highways",
            "Battery costs drop to record lows for EVs",
            "Major automaker commits to electric-only future"
        ],
        "artificial intelligence": [
            "AI breakthrough in medical diagnosis accuracy",
            "New AI model shows remarkable language understanding",
            "Tech giants invest billions in AI research",
            "AI-powered automation transforms manufacturing",
            "Breakthrough AI system solves complex scientific problems"
        ],
        "climate change": [
            "Global temperatures reach new record highs",
            "Renewable energy adoption accelerates worldwide",
            "Climate summit reaches historic agreement",
            "New carbon capture technology shows promise",
            "Extreme weather events increase in frequency"
        ]
    }
    
    # Default headlines if topic not found
    default_headlines = [
        f"Breaking news about {topic} developments",
        f"Latest {topic} research shows promising results",
        f"Industry experts discuss {topic} trends",
        f"New {topic} regulations announced",
        f"Global {topic} market continues to grow"
    ]
    
    # Get headlines for the topic (case-insensitive)
    topic_lower = topic.lower()
    headlines = simulated_headlines.get(topic_lower, default_headlines)
    
    return json.dumps(headlines)


def fetcher_agent(state: State):
    """Extract topic from user input and fetch headlines."""
    # Extract user input from messages (ONLY thing evaluator provides)
    user_input = state["messages"][0].content if state["messages"] else ""
    
    # Use user input as the topic
    topic = user_input.strip()
    
    # Get headlines using the news fetch tool
    headlines_json = news_fetch_tool.invoke({"topic": topic})
    
    # Create response message
    response_content = headlines_json
    
    return {
        "messages": [AIMessage(content=response_content)],
        "topic": topic,
        "headlines_str": headlines_json
    }


def analyzer_agent(state: State):
    """Parse headlines and find words appearing ≥2 times."""
    # Get headlines from state with default
    headlines_str = state.get("headlines_str", "[]")
    
    try:
        # Parse the JSON string to get headlines list
        headlines = json.loads(headlines_str)
    except (json.JSONDecodeError, TypeError):
        headlines = []
    
    # Count word occurrences across all headlines
    word_count: dict[str, int] = {}
    for headline in headlines:
        if isinstance(headline, str):
            # Split into words and clean them
            words = headline.lower().replace(',', '').replace('.', '').split()
            for word in words:
                # Filter out common words and short words
                if len(word) > 2 and word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'her', 'way', 'many', 'then', 'them', 'well', 'were']:
                    word_count[word] = word_count.get(word, 0) + 1
    
    # Find words that appear 2 or more times
    trends = [word for word, count in word_count.items() if count >= 2]
    
    # Serialize trends to JSON string
    trends_json = json.dumps(trends)
    
    # Create response message
    response_content = trends_json
    
    return {
        "messages": [AIMessage(content=response_content)],
        "trends_str": trends_json
    }


def reporter_agent(state: State):
    """Create final alert based on trends and topic."""
    # Get trends and topic from state with defaults
    trends_str = state.get("trends_str", "[]")
    topic = state.get("topic", "unknown topic")
    
    try:
        # Parse the trends JSON string
        trends = json.loads(trends_str)
    except (json.JSONDecodeError, TypeError):
        trends = []
    
    # Create alert object based on whether trends exist
    if trends and len(trends) > 0:
        # Format keywords for summary
        if len(trends) == 1:
            keywords_text = trends[0]
        elif len(trends) == 2:
            keywords_text = f"{trends[0]} and {trends[1]}"
        else:
            keywords_text = f"{', '.join(trends[:-1])}, and {trends[-1]}"
        
        alert = {
            "trend_found": True,
            "trend_keywords": trends,
            "alert_summary": f"In the latest headlines on {topic}, we saw repeated mentions of {keywords_text}."
        }
    else:
        alert = {
            "trend_found": False,
            "alert_summary": f"No new trend detected for {topic}."
        }
    
    # Serialize alert to JSON string
    alert_json = json.dumps(alert)
    
    # Create response message
    response_content = alert_json
    
    return {
        "messages": [AIMessage(content=response_content)]
    }


# Build the StateGraph
graph_builder = StateGraph(State)

# Add nodes for the three agents
graph_builder.add_node("fetcher", fetcher_agent)
graph_builder.add_node("analyzer", analyzer_agent)
graph_builder.add_node("reporter", reporter_agent)

# Add edges to create sequential flow: START -> fetcher -> analyzer -> reporter -> END
graph_builder.add_edge(START, "fetcher")
graph_builder.add_edge("fetcher", "analyzer")
graph_builder.add_edge("analyzer", "reporter")
graph_builder.add_edge("reporter", END)

# Compile the graph and export as 'app' (REQUIRED for evaluator)
app = graph_builder.compile()

