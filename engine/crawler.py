import re
import asyncio
import aiohttp
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

class WebSpider:
    def __init__(self, indexer, max_concurrency=5, request_timeout=6):
        self.indexer = indexer
        self.max_concurrency = max_concurrency
        self.timeout = request_timeout
        self.visited_urls = set()
        self.semaphore = asyncio.Semaphore(max_concurrency)
        self.headers = {
            "User-Agent": "AiraBot/1.0 (+https://airagroup.technology/bot; Sovereign Web Search Engine)"
        }

    def is_valid_url(self, url):
        try:
            parsed = urlparse(url)
            if parsed.scheme not in ("http", "https"):
                return False
            ext = url.split("?")[0].lower()
            skip_exts = (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".tar", ".gz", ".mp4", ".mp3", ".css", ".js")
            if any(ext.endswith(x) for x in skip_exts):
                return False
            return True
        except Exception:
            return False

    async def fetch_and_index(self, session, url):
        if url in self.visited_urls or not self.is_valid_url(url):
            return []
        self.visited_urls.add(url)

        try:
            async with self.semaphore:
                async with session.get(url, headers=self.headers, timeout=self.timeout) as resp:
                    if resp.status != 200:
                        return []
                    content_type = resp.headers.get("Content-Type", "")
                    if "text/html" not in content_type:
                        return []

                    html = await resp.text(errors="ignore")

            soup = BeautifulSoup(html, "html.parser")

            # Remove scripts and styles
            for script in soup(["script", "style", "noscript", "svg", "header", "footer", "nav"]):
                script.extract()

            # Extract Title
            title = soup.title.string.strip() if soup.title and soup.title.string else url

            # Extract Meta Description
            snippet = ""
            meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find("meta", attrs={"property": "og:description"})
            if meta_desc and meta_desc.get("content"):
                snippet = meta_desc["content"].strip()

            # Extract main text
            text_elements = soup.find_all(['p', 'h1', 'h2', 'h3', 'article', 'section'])
            body_text = " ".join([elem.get_text() for elem in text_elements])
            clean_text = re.sub(r'\s+', ' ', body_text).strip()

            if not snippet and clean_text:
                snippet = clean_text[:220] + ("..." if len(clean_text) > 220 else "")

            # Index into memory
            self.indexer.add_document(
                url=url,
                title=title,
                content=clean_text[:15000], # index top 15KB of text per page
                snippet=snippet
            )

            # Discover outgoing links
            out_links = []
            for a_tag in soup.find_all("a", href=True):
                full_url = urljoin(url, a_tag["href"]).split("#")[0]
                if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                    out_links.append(full_url)

            return out_links[:10] # Return top 10 links to explore

        except Exception as e:
            # Silently pass timeouts or network drops
            return []

    async def crawl_seeds(self, seeds, max_pages=50):
        queue = list(seeds)
        indexed_count = 0

        async with aiohttp.ClientSession() as session:
            while queue and indexed_count < max_pages:
                batch = queue[:self.max_concurrency]
                queue = queue[self.max_concurrency:]

                tasks = [self.fetch_and_index(session, url) for url in batch]
                results = await asyncio.gather(*tasks)

                for discovered in results:
                    for link in discovered:
                        if link not in self.visited_urls and link not in queue:
                            queue.append(link)

                indexed_count += len(batch)

        self.indexer.save()
        return len(self.indexer.documents)
