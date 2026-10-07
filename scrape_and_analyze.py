import asyncio
import anthropic
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, CacheMode


class CrawlError(Exception):
    """Raised when Crawl4AI cannot fetch or render a page."""


class ClaudeRefusalError(Exception):
    """Raised when Claude declines to answer (stop_reason == "refusal")."""


async def scrape_url(url: str) -> str:
    """Renders the webpage with Playwright and returns cleaned Markdown."""
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Bypass cache to fetch fresh data
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(url=url, config=run_config)

        if not result.success:
            raise CrawlError(f"Failed to crawl {url}: {result.error_message}")

        markdown = str(result.markdown or "")
        print(f" Successfully scraped {url} ({len(markdown)} characters)")
        return markdown


def analyze_with_claude(markdown_content: str, prompt: str) -> str:
    """Sends the scraped Markdown content to Claude for extraction or analysis."""
    client = anthropic.Anthropic()  # Reads ANTHROPIC_API_KEY (or an `ant auth login` profile)

    system_instruction = (
        "You are an expert web data analyst. "
        "You will receive raw markdown extracted from a web page. "
        "Analyze it thoroughly and answer the user prompt accurately."
    )

    response = client.beta.messages.create(
        model="claude-opus-5-5",
        max_tokens=16000,
        output_config={"effort": "medium"},
        # Retry on a substitute model if a safety classifier declines the request
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        system=system_instruction,
        messages=[
            {
                "role": "user",
                "content": f"User Prompt: {prompt}\n\nWebpage Content:\n{markdown_content}"
            }
        ]
    )

    if response.stop_reason == "refusal":
        raise ClaudeRefusalError(f"Claude declined the request: {response.stop_details}")

    return "".join(block.text for block in response.content if block.type == "text")


async def main():
    # Target URL and extraction prompt
    target_url = "https://news.ycombinator.com"
    prompt = "Extract the top 5 stories listed on this page, including their points and author if available. Format as a bulleted list."

    print(f"Scraping {target_url} using Crawl4AI...")
    scraped_markdown = await scrape_url(target_url)

    print("Sending content to Claude API...")
    analysis = analyze_with_claude(scraped_markdown, prompt)

    print("\n--- Claude Analysis Response ---")
    print(analysis)


if __name__ == "__main__":
    asyncio.run(main())
