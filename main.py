from fastmcp import FastMCP
import json
from typing import Dict, Any, List

# Initialize the MCP server with a descriptive name
# mcp = FastMCP(
#     "BMICalculator",
#     # For remote hosting & ChatGPT, stateless HTTP / streamable HTTP is preferred
#     stateless_http=True,
# )
mcp = FastMCP("BMICalculator")

# --------------------------------------------------------------------
# 1) Core BMI tool (your original logic, kept as-is)
# --------------------------------------------------------------------


@mcp.tool()
def calculate_bmi(weight_kg: float, height_cm: float) -> Dict[str, Any]:
    """
    Calculate Body Mass Index (BMI) given weight (kg) and height (cm).
    Returns a dictionary with BMI value and category.
    """
    if height_cm <= 0 or weight_kg <= 0:
        return {
            "status": "error",
            "message": "Height and weight must be positive numbers.",
        }

    height_m = height_cm / 100.0
    bmi = weight_kg / (height_m**2)

    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obesity"

    return {
        "status": "success",
        "bmi": round(bmi, 2),
        "category": category,
    }


# --------------------------------------------------------------------
# 2) Minimal "document model" so we can implement search/fetch
#    in the format ChatGPT expects.
#    Think of this as a virtual catalog of "BMI docs".
# --------------------------------------------------------------------


DOCUMENTS: List[Dict[str, Any]] = [
    {
        "id": "bmi-intro",
        "title": "BMI basics and categories",
        "url": "https://example.com/bmi-intro",
        "text": (
            "Body Mass Index (BMI) is a simple calculation using a person's "
            "height and weight. It helps categorize underweight, normal "
            "weight, overweight, and obesity."
        ),
        "metadata": {"topic": "bmi", "version": "1.0.0"},
    },
    {
        "id": "bmi-how-to-use-tool",
        "title": "How to use the BMI Calculator MCP tool",
        "url": "https://example.com/bmi-calculator-mcp",
        "text": (
            "Use the calculate_bmi tool by providing weight in kilograms "
            "and height in centimeters. The tool returns the BMI value and "
            "category."
        ),
        "metadata": {"topic": "bmi", "version": "1.0.0"},
    },
]


def _search_docs(query: str) -> List[Dict[str, Any]]:
    """
    Naive search over DOCUMENTS.
    Returns a list of {id, title, url}.
    """
    query_lower = query.lower()
    results = []

    for doc in DOCUMENTS:
        if (
            query_lower in doc["title"].lower()
            or query_lower in doc["text"].lower()
            or query_lower in doc["metadata"].get("topic", "").lower()
        ):
            results.append(
                {
                    "id": doc["id"],
                    "title": doc["title"],
                    "url": doc["url"],
                }
            )

    return results


def _fetch_doc(doc_id: str) -> Dict[str, Any]:
    """
    Fetch a full document dict by id or raise an error.
    """
    for doc in DOCUMENTS:
        if doc["id"] == doc_id:
            return doc
    raise ValueError(f"Document with id {doc_id!r} not found")


# --------------------------------------------------------------------
# 3) ChatGPT-compatible `search` and `fetch` tools
#    IMPORTANT: signatures and return shape follow the pattern
#    ChatGPT expects (single string arg, JSON string return).
# --------------------------------------------------------------------


@mcp.tool()
def search(query: str) -> str:
    """
    ChatGPT / MCP 'search' tool.

    Accepts:
        query: search string

    Returns:
        JSON string with:
        {
            "results": [
                {"id": str, "title": str, "url": str},
                ...
            ]
        }
    """
    results = _search_docs(query)
    payload = {"results": results}
    return json.dumps(payload)


@mcp.tool()
def fetch(doc_id: str) -> str:
    """
    ChatGPT / MCP 'fetch' tool.

    Accepts:
        doc_id: id of a document from search results

    Returns:
        JSON string with full document:
        {
            "id": str,
            "title": str,
            "text": str,
            "url": str,
            "metadata": {...}
        }
    """
    doc = _fetch_doc(doc_id)
    return json.dumps(doc)


# --------------------------------------------------------------------
# 4) Optional resource: server info (kept from your original code)
# --------------------------------------------------------------------


@mcp.resource("info://server")
def server_info() -> str:
    """
    Get information about this server.
    """
    info = {
        "name": "BMI Calculator MCP Server",
        "version": "1.0.0",
        "description": "A simple MCP server for BMI calculation.",
        "tools": ["calculate_bmi", "search", "fetch"],
        "author": "Your Name",
    }
    return json.dumps(info, indent=2)


# --------------------------------------------------------------------
# 5) Server entrypoint
#    For FastMCP Cloud, use streamable-http / stateless HTTP.
# --------------------------------------------------------------------


if __name__ == "__main__":
    # For local testing you can run HTTP or streamable-http.
    # FastMCP Cloud will still call mcp.run() with HTTP/streamable HTTP.
    # mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
    mcp.run(transport="sse", host="0.0.0.0", port=8000)
