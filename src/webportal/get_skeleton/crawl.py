#!/usr/bin/env python3
"""
Fast Website Skeleton Crawler with JavaScript Support using Playwright
Extracts ~90% of a website's structure quickly with concurrent browser contexts
"""

import argparse
import asyncio
import json
import re
import time
from collections import defaultdict
from urllib.parse import urlparse

from playwright.async_api import Page, async_playwright
from pydantic import BaseModel


class TemplateSegment(BaseModel):
    pass


class VariableTemplateSegment(TemplateSegment):
    examples: set[str] = set()


class FixedTemplateSegment(TemplateSegment):
    example: str


class Template(BaseModel):
    segments: list[TemplateSegment]


class FastJSCrawler:
    def __init__(self, start_url, max_pages=100, max_depth=5, concurrency=10):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.concurrency = concurrency

        self.visited = set()
        self.to_visit = asyncio.Queue()
        self.site_structure = defaultdict(set)
        self.page_titles = {}
        self.generic_url_patterns = set()  # Store discovered URL patterns
        self.pattern_templates: list[
            Template
        ] = []  # Store structural templates with examples: {template: {position: [examples]}}
        self.path_structures = defaultdict(
            set
        )  # Track path lengths for each position's segments
        self.semaphore = asyncio.Semaphore(concurrency)

    def is_static_asset(self, url: str) -> bool:
        """Check if URL points to a static asset that shouldn't be crawled"""
        static_extensions = {
            ".css",
            ".js",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            ".pdf",
            ".zip",
            ".tar",
            ".gz",
            ".mp4",
            ".mp3",
            ".webm",
            ".woff",
            ".woff2",
            ".ttf",
            ".eot",
            ".xml",
            ".json",
            ".txt",
            ".webmanifest",
        }

        parsed = urlparse(url)
        path = parsed.path.lower()

        # Check file extension
        for ext in static_extensions:
            if path.endswith(ext):
                return True

        # Check for common static asset paths
        static_paths = [
            "/static/",
            "/assets/",
            "/css/",
            "/js/",
            "/images/",
            "/img/",
            "/fonts/",
        ]
        if any(static_path in path for static_path in static_paths):
            return True

        return False

    def is_same_domain_or_subdomain(self, url_domain: str) -> bool:
        """Check if a domain is the same or a subdomain of the original domain"""
        if url_domain == self.domain:
            return True

        # Handle subdomains (e.g., idp.nature.com should match nature.com)
        if url_domain.endswith("." + self.domain):
            return True

        # Handle www variations
        if url_domain.startswith("www.") and url_domain[4:] == self.domain:
            return True
        if self.domain.startswith("www.") and url_domain == self.domain[4:]:
            return True

        return False

    async def handle_cookie_banners(self, page: Page):
        """Handle common cookie banners and consent dialogs"""
        try:
            # Wait a moment for banners to load
            await asyncio.sleep(1)

            # Common cookie banner selectors and their accept buttons
            cookie_selectors = [
                # Generic patterns
                '[data-cc-action="accept"]',
                '[data-action="accept"]',
                'button[id*="accept"]',
                'button[class*="accept"]',
                'button:has-text("Accept")',
                'button:has-text("Accept all")',
                'button:has-text("Allow all")',
                'button:has-text("I agree")',
                'button:has-text("OK")',
                # Specific to nature.com and common providers
                ".cc-banner__button-accept",
                "#onetrust-accept-btn-handler",
                "#hs-eu-confirmation-button",
                ".osano-cm-accept-all",
                ".cookie-consent-accept",
                ".gdpr-accept",
                # Other common patterns
                '.btn:has-text("Accept")',
                '.button:has-text("Accept")',
                'a:has-text("Accept")',
                '[aria-label*="Accept"]',
                '[title*="Accept"]',
            ]

            # Try each selector
            for selector in cookie_selectors:
                try:
                    # Check if element exists and is visible
                    element = await page.query_selector(selector)
                    if element:
                        is_visible = await element.is_visible()
                        if is_visible:
                            await element.click()
                            # Wait for the banner to disappear
                            await asyncio.sleep(0.5)
                            print(
                                f"Clicked cookie accept button with selector: {selector}"
                            )
                            return
                except Exception:
                    # Continue to next selector if this one fails
                    continue

        except Exception as e:
            # Don't let cookie handling break the crawler
            print(f"Cookie banner handling failed: {str(e)[:50]}")

    def _replace_with_generic_pattern_if_necessary(self, url: str) -> str:
        """Apply generic pattern detection to individual URL segments"""
        # Handle the protocol part separately to preserve double slashes
        if "://" in url:
            protocol_part, path_part = url.split("://", 1)
            protocol_prefix = protocol_part + "://"
        else:
            protocol_prefix = ""
            path_part = url

        segments = path_part.split("/")

        # Pattern definitions for individual segments (without slashes)
        segment_patterns = [
            # UUIDs
            (
                r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$",
                "{uuid}",
            ),
            # Alphanumeric hashes (like commit hashes, session IDs) - must contain at least one letter and be 8+ chars
            (r"^[a-f0-9]{8,}$", "{hash}"),
            # Numeric IDs
            (r"^\d+$", "{id}"),
            # Version numbers (like v1.2.3, 2024.1.1)
            (r"^v?\d+(\.\d+)*$", "{version}"),
            # Version numbers
            (r"^(?!.*[a-zA-Z]{3}).*$", "{id}"),
        ]

        # Apply pattern matching to each segment
        for i, segment in enumerate(segments):
            if segment:  # Skip empty segments
                for pattern_regex, pattern_name in segment_patterns:
                    if re.match(pattern_regex, segment):
                        segments[i] = pattern_name
                        break

        return protocol_prefix + "/".join(segments)

    def log_new_fixed_template(self, url: str):
        """Log a new fixed template, applying generic pattern detection to segments"""
        segments = [seg for seg in url.split("/") if seg]
        template_segments = []

        for segment in segments:
            template_segments.append(FixedTemplateSegment(example=segment))

        self.pattern_templates.append(Template(segments=template_segments))

    def matches_existing_template(self, url: str) -> int:
        """Check if a specific URL path matches any of our discovered templates. Criterion for belonging to a template:
        - have the same number as segments
        - segments should match except for variable positions. There will be at max one variable position (assumption)

        Returns the template index if the url matches an existing template, -1 otherwise.
        """
        segments = [seg for seg in url.split("/") if seg]
        if not segments:
            return -1

        for template_index, template in enumerate(self.pattern_templates):
            template_segments = template.segments

            if len(segments) != len(template_segments):
                continue

            # Cases here:
            # 1. The url belongs to an existing template:
            # Either at one variable part difference: should be only one variabel part, and append it to the variables
            # Or matches all segments except for one, and the exisiting template has only fixed parts else : then make it variable
            # 2. The url does not belong to an existing template, it's new and should be visited.

            # Note which segments are same vs different:

            segment_identity: list[int] = [-1] * len(segments)

            for segment_index, (segment, template_segment) in enumerate(
                zip(segments, template_segments)
            ):
                if isinstance(template_segment, FixedTemplateSegment):
                    segment_identity[segment_index] = (
                        1 if segment == template_segment.example else 0
                    )
                else:
                    # Just add the segment value to variable segment examples if not there
                    if segment not in template_segment.examples:
                        template_segment.examples.add(segment)
                    segment_identity[segment_index] = 1

            if sum(segment_identity) == len(segments):
                # The url directly belongs to this existing template: return the template index
                return template_index

            if sum([el == 0 for el in segment_identity]) == 1:
                # There is one difference : see if it can be conciled. It will be conciled only if the other segments are all fixed
                differing_segment_index = segment_identity.index(0)
                if (
                    sum(
                        [
                            isinstance(template_segment, VariableTemplateSegment)
                            for segment_index, template_segment in enumerate(
                                template_segments
                            )
                            if not segment_index == differing_segment_index
                        ]
                    )
                    <= 1
                ):
                    if isinstance(
                        template_segments[differing_segment_index],
                        VariableTemplateSegment,
                    ):
                        # Just append the new segment to the variable segment
                        template_segments[differing_segment_index].examples.add(segment)
                        return template_index
                    elif isinstance(
                        template_segments[differing_segment_index], FixedTemplateSegment
                    ):
                        # We've discovered a new variable segment!
                        template_segments[differing_segment_index] = (
                            VariableTemplateSegment(
                                examples={
                                    segment,
                                    template_segments[differing_segment_index].example,
                                }
                            )
                        )
                        return template_index
        return -1

    def normalize_url(self, url: str) -> str:
        """Normalize URL by removing/parameterizing query parameters and recognizing patterns"""
        parsed = urlparse(url)
        path = parsed.path
        return parsed.scheme + "://" + parsed.netloc + path

    async def extract_link_patterns(self, page: Page, url, current_depth):
        """Extract all link patterns from the page after JavaScript execution, merges them with existing patterns"""
        new_links = []
        try:
            # Wait for initial load
            await page.wait_for_load_state("networkidle", timeout=10000)
            # await page.wait_for_selector("body", timeout=15000)

            # visible_text = await page.evaluate("() => document.body.innerHTML")
            # print(f"\n=== VISIBLE TEXT FOR {url} ===")
            # print(visible_text[:10000])  # First 1000 characters
            # print("=" * 50)

            # Extract title
            title = await page.title()
            if title:
                self.page_titles[url] = title.strip()

            # Extract all links using JavaScript
            links = await page.evaluate("""
                () => {
                    const links = new Set();
                    // Get all anchor tags
                    document.querySelectorAll('a[href]').forEach(a => {
                        links.add(a.href);
                    });
                    // Get links from JavaScript navigation elements
                    document.querySelectorAll('[onclick], [data-href], [data-url]').forEach(el => {
                        const onclick = el.getAttribute('onclick');
                        if (onclick) {
                            const match = onclick.match(/(?:location\\.href|window\\.location|navigate)\\s*=\\s*['"]([^'"]+)['"]/);
                            if (match) links.add(new URL(match[1], window.location.href).href);
                        }
                        const dataHref = el.getAttribute('data-href') || el.getAttribute('data-url');
                        if (dataHref) links.add(new URL(dataHref, window.location.href).href);
                    });
                    // Get router links (React, Vue, etc)
                    document.querySelectorAll('[to], [href^="/"], [href^="./"], [href^="../"]').forEach(el => {
                        const href = el.getAttribute('to') || el.getAttribute('href');
                        if (href) links.add(new URL(href, window.location.href).href);
                    });
                    return Array.from(links);
                }
            """)

            # Filter links to same domain and apply normalization
            for link in links:
                if link in self.visited:
                    continue

                parsed = urlparse(link)
                if self.is_same_domain_or_subdomain(parsed.netloc):
                    # Remove fragment
                    clean_url = link.split("#")[0].split("?")[0]

                    # Skip static assets
                    if self.is_static_asset(clean_url):
                        continue

                    # Check if this URL matches an existing structural template
                    normalized_url = self.normalize_url(clean_url)
                    normalized_url = self._replace_with_generic_pattern_if_necessary(
                        normalized_url
                    )
                    matching_template_index = self.matches_existing_template(
                        normalized_url
                    )
                    if matching_template_index != -1:
                        # Skip this URL as it matches a known pattern already
                        continue
                    else:
                        if "?" in normalized_url:
                            raise ValueError(
                                f"URL {normalized_url} has a query parameter, which is not supported"
                            )
                        new_links.append(normalized_url)
                        self.log_new_fixed_template(normalized_url)
                        if current_depth < self.max_depth:
                            await self.to_visit.put((normalized_url, current_depth + 1))
                            print(
                                "Remaining links to visit: ",
                                self.to_visit.qsize(),
                                self.to_visit,
                            )
                            if self.to_visit.qsize() > 25:
                                print(self.pattern_templates)
            return new_links

        except Exception as e:
            # Return empty list on error to keep crawling
            print(f"Error extracting links from {url}: {str(e)[:50]}")
            return new_links

    async def crawl_page(self, browser, url, depth):
        """Crawl a single page"""
        async with self.semaphore:
            if url in self.visited or len(self.visited) >= self.max_pages:
                return

            self.visited.add(url)

            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                extra_http_headers={"Cookie": "cc-accept=true"},
            )
            page = await context.new_page()

            try:
                # Navigate to the page
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)

                # Handle cookie banners and consent dialogs
                await self.handle_cookie_banners(page)

                # Extract links after JS execution
                new_links = await self.extract_link_patterns(page, url, depth)

                # Count patterns discovered
                pattern_count = len(self.generic_url_patterns) + len(
                    self.pattern_templates
                )
                print(
                    f"Crawled: {url} ({len(self.visited)}/{self.max_pages}) - Found {len(new_links)} new links, totaling {pattern_count} patterns so far"
                )

            except Exception as e:
                print(f"Error crawling {url}: {str(e)[:50]}")
                # raise e
            finally:
                await context.close()

    async def worker(self, browser):
        """Worker that processes URLs from the queue"""
        while True:
            try:
                url, depth = await asyncio.wait_for(self.to_visit.get(), timeout=2.0)
                await self.crawl_page(browser, url, depth)
            except asyncio.TimeoutError:
                # No more URLs to process
                if self.to_visit.empty():
                    break

    async def crawl(self):
        """Main crawling function"""
        print(f"Starting crawl of {self.start_url}")
        print(
            f"Max pages: {self.max_pages}, Max depth: {self.max_depth}, Concurrency: {self.concurrency}"
        )
        print("-" * 70)

        async with async_playwright() as p:
            # Launch browser in headless mode
            browser = await p.chromium.launch(
                headless=True, args=["--disable-blink-features=AutomationControlled"]
            )

            # Add start URL to queue
            await self.to_visit.put((self.start_url, 0))

            # Create workers
            workers = [
                asyncio.create_task(self.worker(browser))
                for _ in range(self.concurrency)
            ]

            # Wait for all workers to finish
            await asyncio.gather(*workers)

            await browser.close()

    def get_statistics(self):
        """Generate crawl statistics"""
        total_links = sum(len(links) for links in self.site_structure.values())

        # Find pages with most links
        pages_by_links = sorted(
            [(url, len(links)) for url, links in self.site_structure.items()],
            key=lambda x: x[1],
            reverse=True,
        )[:10]

        # Path depth analysis
        depth_distribution = defaultdict(int)
        for url in self.visited:
            path = urlparse(url).path
            depth = path.count("/")
            depth_distribution[depth] += 1

        return {
            "pages_crawled": len(self.visited),
            "total_links_found": total_links,
            "pages_with_most_links": pages_by_links,
            "depth_distribution": dict(depth_distribution),
        }

    def export_structure(self, format="tree"):
        """Export the site structure in different formats"""
        if format == "tree":
            return self._export_tree()
        elif format == "json":
            return self._export_json()
        elif format == "urls":
            return self._export_urls()
        elif format == "sitemap":
            return self._export_sitemap()

    def _export_tree(self):
        """Export as a tree structure"""
        result = []
        result.append(f"Site Structure for {self.domain}")
        result.append("=" * 50)
        result.append("")

        # Group URLs by path structure for tree display, avoiding duplicates
        path_to_title = {}

        # Add structural pattern templates with examples first (higher priority)
        template_paths_added = set()
        for template in self.pattern_templates:
            template_path = ""
            for segment in template.segments:
                if isinstance(segment, FixedTemplateSegment):
                    if segment.example != "https:":
                        template_path += segment.example + "/"
                else:
                    template_path += (
                        "["
                        + (
                            "|".join(list(segment.examples)[:3])
                            + ("|..." if len(segment.examples) > 3 else "")
                        )
                        + "]"
                        + "/"
                    )
            if template_path and template_path not in path_to_title:
                path_to_title[template_path] = "Template Pattern"
                template_paths_added.add(template_path.rstrip("/"))

        # Add discovered generic URL patterns only if they don't overlap with templates
        for pattern in sorted(self.generic_url_patterns):
            parsed = urlparse(pattern)
            path = parsed.path.rstrip("/")
            # Only add if path doesn't conflict with existing templates or paths
            if path and path not in path_to_title and path not in template_paths_added:
                # Check if this generic pattern semantically overlaps with any template
                path_to_title[path] = "URL Pattern"

        # Convert to list and sort paths
        paths = list(path_to_title.items())
        paths.sort(key=lambda x: (x[0].count("/"), x[0]))

        # Display tree with proper tree characters
        for i, (path, title) in enumerate(paths):
            is_last = i == len(paths) - 1
            tree_char = "└──" if is_last else "├──"

            result.append(f"{tree_char} {path} - {title}")

        return "\n".join(result)

    def _export_json(self):
        """Export as JSON"""
        return json.dumps(
            {
                "domain": self.domain,
                "start_url": self.start_url,
                "pages_crawled": len(self.visited),
                "statistics": self.get_statistics(),
                "structure": {
                    url: {"title": self.page_titles.get(url, ""), "links": list(links)}
                    for url, links in self.site_structure.items()
                },
            },
            indent=2,
        )

    def _export_urls(self):
        """Export as simple URL list"""
        return "\n".join(sorted(self.visited))

    def _export_sitemap(self):
        """Export as XML sitemap format"""
        result = ['<?xml version="1.0" encoding="UTF-8"?>']
        result.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        for url in sorted(self.visited):
            result.append("  <url>")
            result.append(f"    <loc>{url}</loc>")
            result.append("  </url>")

        result.append("</urlset>")
        return "\n".join(result)


def test_crawler_logs_variable_template():
    crawler = FastJSCrawler(
        "https://arxiv.org/abs/2507.09001",
        max_pages=10,
        max_depth=5,
        concurrency=1,
    )
    crawler.log_new_fixed_template("https://arxiv.org/abs/")
    assert crawler.matches_existing_template("https://arxiv.org/abs/") == 0
    assert crawler.matches_existing_template("https://arxiv.org/pdf/") == 0
    assert crawler.pattern_templates[0].segments[-1].examples == {"abs", "pdf"}
    assert crawler.matches_existing_template("https://arxiv.org/html/") == 0
    assert crawler.pattern_templates[0].segments[-1].examples == {"abs", "pdf", "html"}

    crawler = FastJSCrawler(
        "https://arxiv.org/abs/2507.09001",
        max_pages=10,
        max_depth=5,
        concurrency=1,
    )
    crawler.log_new_fixed_template("https://arxiv.org/abs/2507.14279")
    assert crawler.matches_existing_template("https://arxiv.org/abs/2507.14280") == 0
    assert crawler.matches_existing_template("https://arxiv.org/abs/2507.14260") == 0

    replaced_url = crawler._replace_with_generic_pattern_if_necessary(
        "https://www.nature.com/naturecareers/job/12841799/687/v1.2.3/139941a0/v12/postdoctoral-researchers-in-experimental-condensed-matter-physics/"
    )
    assert (
        replaced_url
        == "https://www.nature.com/naturecareers/job/{hash}/{id}/{version}/{hash}/{version}/postdoctoral-researchers-in-experimental-condensed-matter-physics/"
    ), replaced_url


async def main():
    test_crawler_logs_variable_template()
    parser = argparse.ArgumentParser(
        description="Fast website skeleton crawler with JavaScript support"
    )
    parser.add_argument(
        "--url", help="Starting URL to crawl", type=str, default="arxiv.org"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=100,
        help="Maximum pages to crawl (default: 100)",
    )
    parser.add_argument(
        "--max-depth", type=int, default=5, help="Maximum depth to crawl (default: 5)"
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=8,
        help="Number of concurrent browser contexts (default: 1)",
    )
    parser.add_argument(
        "--format",
        choices=["tree", "json", "urls", "sitemap"],
        default="tree",
        help="Output format",
    )
    parser.add_argument("--output", help="Output file (optional)")

    args = parser.parse_args()

    # Ensure URL has scheme
    if not args.url.startswith(("http://", "https://")):
        args.url = "https://" + args.url

    start_time = time.time()

    # Create and run crawler
    crawler = FastJSCrawler(
        args.url,
        max_pages=args.max_pages,
        max_depth=args.max_depth,
        concurrency=args.concurrency,
    )

    try:
        await crawler.crawl()
    except KeyboardInterrupt:
        print("\n\nCrawl interrupted by user")

    elapsed = time.time() - start_time

    # Print statistics
    print("\n" + "=" * 70)
    stats = crawler.get_statistics()
    print(f"Crawl completed in {elapsed:.2f} seconds")
    print(f"Pages crawled: {stats['pages_crawled']}")
    print(f"Pages per second: {stats['pages_crawled'] / elapsed:.2f}")
    print(f"Total unique links found: {stats['total_links_found']}")
    print("\nDepth distribution:")
    for depth, count in sorted(stats["depth_distribution"].items()):
        print(f"  Level {depth}: {count} pages")

    # Export results
    output = crawler.export_structure(args.format)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"\nResults saved to {args.output}")
    else:
        print("\n" + output)


if __name__ == "__main__":
    # Install playwright browsers if not already installed
    try:
        asyncio.run(main())
    except Exception as e:
        if "playwright install" in str(e):
            print("Please install Playwright browsers first:")
            print("  playwright install chromium")
        else:
            raise
