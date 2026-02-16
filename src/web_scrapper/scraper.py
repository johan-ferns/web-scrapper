"""
Web Scraper module for extracting content from web pages using Playwright.

This module provides functions to scrape web pages with a headless browser,
suitable for air-gapped deployments with bundled browser binaries.
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

def scrape_page(
    url: str,
    headless: bool = True,
    timeout: int = 30000,
    wait_for_selector: Optional[str] = None
) -> Dict[str, Any]:
    """
    Scrape content from a web page using Playwright.
    
    Args:
        url: The URL to scrape
        headless: Whether to run browser in headless mode (default: True)
        timeout: Page load timeout in milliseconds (default: 30000)
        wait_for_selector: Optional CSS selector to wait for before scraping
        
    Returns:
        Dictionary containing:
            - success: bool indicating if scraping was successful
            - url: the scraped URL
            - title: page title
            - content: text content of the page
            - html: full HTML content
            - error: error message if success is False
    """
    result = {
        "success": False,
        "url": url,
        "title": "",
        "content": "",
        "html": "",
        "error": ""
    }
    
    try:
        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()
            
            # Navigate to URL
            page.goto(url, timeout=timeout, wait_until="networkidle")
            
            # Wait for specific selector if provided
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector, timeout=timeout)
            
            # Extract content
            result["title"] = page.title()
            result["content"] = page.inner_text("body")
            result["html"] = page.content()
            result["success"] = True
            
            # Close browser
            browser.close()
            
    except PlaywrightTimeoutError as e:
        result["error"] = f"Timeout error: {str(e)}"
    except Exception as e:
        result["error"] = f"Error scraping page: {str(e)}"
    
    return result


def scrape_statistics_canada_daily(output_file: Optional[Path] = None) -> Dict[str, Any]:
    """
    Example function to scrape Statistics Canada Daily release.
    
    Args:
        output_file: Optional path to save the scraped content as JSON
        
    Returns:
        Dictionary with scraped content
    """
    url = "https://www150.statcan.gc.ca/n1/daily-quotidien/260216/dq260216a-eng.htm"
    
    print(f"Scraping Statistics Canada Daily: {url}")
    result = scrape_page(
        url=url,
        wait_for_selector="main"  # Wait for main content to load
    )
    
    if result["success"]:
        print(f"✓ Successfully scraped: {result['title']}")
        print(f"✓ Content length: {len(result['content'])} characters")
        
        # Save to file if specified
        if output_file:
            output_file = Path(output_file)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as JSON (without full HTML to keep file smaller)
            save_data = {
                "url": result["url"],
                "title": result["title"],
                "content": result["content"]
            }
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Saved to: {output_file}")
    else:
        print(f"✗ Error: {result['error']}")
    
    return result


if __name__ == "__main__":
    # Example usage
    output_path = Path("output") / "statcan_daily.json"
    scrape_statistics_canada_daily(output_file=output_path)