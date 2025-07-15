# Multi‑Agent News‑Trend Alert System

A LangGraph-based pipeline that fetches news headlines, analyzes emerging trends, and generates alert summaries—all in a modular, multi‑agent workflow.

## Features

- **Fetcher Agent**  
  Retrieves the top 5 headlines for a given topic (via a news‑fetch tool).  
- **Analyzer Agent**  
  Parses those headlines and spots any keywords appearing in at least two headlines.  
- **Reporter Agent**  
  Composes a JSON alert indicating whether a trend was found, listing the keywords, and writing a human‑readable summary. It prints a string at the end will all of the information.

## Architecture

START
└─► fetcher (returns string of headlines)
└─► analyzer (returns string of trends)
└─► reporter (returns final alert string)
└─► END
