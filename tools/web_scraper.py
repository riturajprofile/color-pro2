from langchain_core.tools import tool
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from logger_config import get_logger

logger = get_logger("web_scraper")

@tool
def get_rendered_html(url: str) -> str:
    """
    Fetch and return the fully rendered HTML of a webpage.

    This function uses Playwright to load a webpage in a headless Chromium
    browser, allowing all JavaScript on the page to execute. Use this for
    dynamic websites that require rendering.

    IMPORTANT RESTRICTIONS:
    - ONLY use this for actual HTML webpages (articles, documentation, dashboards).
    - DO NOT use this for direct file links (URLs ending in .csv, .pdf, .zip, .png).
      Playwright cannot render these and will crash. Use the 'download_file' tool instead.

    Parameters
    ----------
    url : str
        The URL of the webpage to retrieve and render.

    Returns
    -------
    str
        The fully rendered and cleaned HTML content.
    """
    logger.info(f"Fetching and rendering URL: {url}")
    try:
        with sync_playwright() as p:
            logger.info("Launching headless Chromium browser")
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # Load the page (let JS execute)
            logger.info(f"Loading page: {url}")
            page.goto(url, wait_until="networkidle")
            logger.info("Page loaded, extracting content")

            # Extract rendered HTML
            content = page.content()

            browser.close()
            logger.info(f"Content extracted successfully ({len(content)} characters)")
            return content

    except Exception as e:
        error_msg = f"Error fetching/rendering page: {str(e)}"
        logger.error(error_msg)
        return error_msg
