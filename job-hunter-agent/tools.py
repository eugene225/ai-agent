import os, re

from crewai.tools import tool
from firecrawl import FirecrawlApp


@tool
def web_search_tool(query: str):
    """
    Web Search Tool.
    Args:
        query: str
            The query to search the web for.
    Returns
        A list of search results with the website content in Markdown format.
    """
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

    try:
        response = app.search(
            query=query,
            limit=5,
            scrape_options={
                "formats": ["markdown"],
            },
        )
    except Exception as exc:
        return f"Error using tool: {exc}"

    cleaned_chunks = []

    for result in (response.web or []):
        if hasattr(result, "markdown"):
            title = getattr(result.metadata_typed, "title", None)
            url = getattr(result.metadata_typed, "url", None) or getattr(result.metadata_typed, "source_url", None)
            markdown = result.markdown or result.summary or ""
        else:
            title = getattr(result, "title", None)
            url = getattr(result, "url", None)
            markdown = getattr(result, "description", "") or ""

        cleaned = re.sub(r"\\+|\n+", "", markdown).strip()
        cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)

        cleaned_result = {
            "title": title,
            "url": url,
            "markdown": cleaned,
        }

        cleaned_chunks.append(cleaned_result)

    return cleaned_chunks