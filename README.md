# Crawl4AI + Claude: scrape_and_analyze.py

Crawls a page with Crawl4AI (headless Chromium), turns it into Markdown and
sends it to Claude for extraction.

## Setup

```bash
pip install -r requirements.txt
crawl4ai-setup      # downloads the Chromium browser Crawl4AI needs
crawl4ai-doctor     # optional: verifies the install
```

`pip install` alone does **not** install the browser; without `crawl4ai-setup`
the crawler cannot start.

## Credentials

Set an API key, or use a profile created with `ant auth login`
(the SDK picks up `ANTHROPIC_PROFILE` / the active profile automatically):

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Run

```bash
python scrape_and_analyze.py
```

Errors: `CrawlError` if the page can't be fetched, `ClaudeRefusalError` if
Claude declines the request.
