import re
import time
from crewai.tools import tool
from crewai_tools import SerperDevTool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

_serper_tool = SerperDevTool(
    n_results=30,
)


def _sanitize_query(query: str) -> str:
    # Serper can reject some advanced operators (ex: site:).
    sanitized = re.sub(r"\bsite:\S+", "", query)
    return " ".join(sanitized.split())


@tool("search_tool")
def search_tool(search_query: str):
    """
    Search the web using Serper.
    Retries with a sanitized query when Serper rejects advanced operators.
    """
    try:
        return _serper_tool.run(search_query=search_query)
    except Exception as exc:  # noqa: BLE001 - surface tool errors to crew
        sanitized = _sanitize_query(search_query)
        if sanitized and sanitized != search_query:
            try:
                return _serper_tool.run(search_query=sanitized)
            except Exception:
                pass
        return f"Search failed: {exc}"


@tool
def scrape_tool(url: str):
    """
    Use this when you need to read the content of a website.
    Returns the content of a website, in case the website is not available, it returns 'No content'.
    Input should be a `url` string. for example (https://www.reuters.com/world/asia-pacific/cambodia-thailand-begin-talks-malaysia-amid-fragile-ceasefire-2025-08-04/)
    """

    print(f"Scrapping URL: {url}")

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        page.goto(url)

        time.sleep(5)

        html = page.content()

        browser.close()

        soup = BeautifulSoup(html, "html.parser")

        unwanted_tags = [
            "header",
            "footer",
            "nav",
            "aside",
            "script",
            "style",
            "noscript",
            "iframe",
            "form",
            "button",
            "input",
            "select",
            "textarea",
            "img",
            "svg",
            "canvas",
            "audio",
            "video",
            "embed",
            "object",
        ]

        for tag in soup.find_all(unwanted_tags):
            tag.decompose()

        content = soup.get_text(separator=" ")

        return content if content != "" else "No content"