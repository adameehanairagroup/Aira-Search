import asyncio
import urllib.request
import urllib.parse
import json
import re
import html
import base64
import time

class WebRetriever:
    """
    Sovereign Live Web Retriever for Aira Search Engine.
    Federated multi-source live web search engine querying:
      1. Wikipedia Full-Text Knowledge Graph (CirrusSearch API)
      2. Microsoft Bing Live Web Index (clean URL decoding)
      3. GitHub Open Source Ecosystem API
      4. DuckDuckGo Organic Index
    """
    def __init__(self, cache_ttl_seconds=900):
        self.cache = {}
        self.cache_ttl = cache_ttl_seconds
        self.default_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9"
        }

    def _decode_bing_url(self, href: str) -> str:
        href = html.unescape(href)
        if "u=" in href:
            try:
                raw = href.split("u=")[1].split("&")[0]
                if raw.startswith("a1"):
                    raw = raw[2:]
                raw += "=" * ((4 - len(raw) % 4) % 4)
                decoded = base64.b64decode(raw).decode("utf-8", errors="ignore")
                if decoded.startswith("http"):
                    return decoded
            except Exception:
                pass
        return href

    def search_wikipedia(self, query: str, max_results: int = 3):
        results = []
        try:
            url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json&srlimit={max_results}"
            req = urllib.request.Request(url, headers={"User-Agent": "AiraSearchBot/1.0 (+https://airagroup.technology)"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                for h in data.get("query", {}).get("search", []):
                    title = h.get("title", "")
                    raw_snippet = h.get("snippet", "")
                    clean_snippet = html.unescape(re.sub(r'<[^>]+>', '', raw_snippet)).strip()
                    wiki_url = f"https://en.wikipedia.org/wiki/{urllib.parse.quote(title.replace(' ', '_'))}"
                    results.append({
                        "title": f"{title} — Wikipedia",
                        "url": wiki_url,
                        "snippet": clean_snippet + ("..." if clean_snippet else ""),
                        "source": "Wikipedia"
                    })
        except Exception:
            pass
        return results

    def search_bing(self, query: str, max_results: int = 8):
        results = []
        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}"
        try:
            req = urllib.request.Request(url, headers=self.default_headers)
            with urllib.request.urlopen(req, timeout=5) as resp:
                page = resp.read().decode("utf-8", errors="ignore")
            
            items = re.findall(r'<li class=\"b_algo\"[^>]*>(.*?)</li>', page, re.DOTALL)
            for it in items:
                tm = re.search(r'<h2><a[^>]+href=\"([^\"]+)\"[^>]*>(.*?)</a></h2>', it, re.DOTALL)
                sm = re.search(r'<p[^>]*>(.*?)</p>', it, re.DOTALL)
                if tm:
                    actual_url = self._decode_bing_url(tm.group(1))
                    if not actual_url.startswith("http") or "bing.com" in actual_url:
                        continue
                    title = html.unescape(re.sub(r'<[^>]+>', '', tm.group(2))).strip()
                    snippet = html.unescape(re.sub(r'<[^>]+>', '', sm.group(1))).strip() if sm else ""
                    results.append({
                        "title": title,
                        "url": actual_url,
                        "snippet": snippet or f"Official resource: {actual_url}",
                        "source": "Web"
                    })
                    if len(results) >= max_results:
                        break
        except Exception:
            pass
        return results

    def search_github(self, query: str, max_results: int = 2):
        results = []
        try:
            url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(query)}&per_page={max_results}"
            req = urllib.request.Request(url, headers={"User-Agent": "AiraSearchBot/1.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                for it in data.get("items", []):
                    title = f"{it.get('full_name')} — GitHub"
                    desc = it.get("description") or f"Open source repository for {query} on GitHub."
                    results.append({
                        "title": title,
                        "url": it.get("html_url"),
                        "snippet": f"{desc} (⭐ {it.get('stargazers_count', 0)} stars)",
                        "source": "GitHub"
                    })
        except Exception:
            pass
        return results

    async def search_live(self, query: str, max_results: int = 20):
        q_norm = query.strip().lower()
        now = time.time()

        if q_norm in self.cache:
            res, expires = self.cache[q_norm]
            if now < expires:
                return res

        # Run independent fetchers concurrently
        t_bing = asyncio.to_thread(self.search_bing, query, 8)
        t_wiki = asyncio.to_thread(self.search_wikipedia, query, 3)
        t_gh = asyncio.to_thread(self.search_github, query, 2)

        res_bing, res_wiki, res_gh = await asyncio.gather(t_bing, t_wiki, t_gh)

        seen_urls = set()
        merged = []

        # 1. Place Wikipedia top article first if available (Encyclopedia Overview)
        if res_wiki:
            top_wiki = res_wiki[0]
            seen_urls.add(top_wiki["url"])
            merged.append(top_wiki)

        # 2. Add organic web search results
        for item in res_bing:
            if item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                merged.append(item)

        # 3. Add GitHub repositories if relevant
        for item in res_gh:
            if item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                merged.append(item)

        # 4. Add remaining Wikipedia entries
        for item in res_wiki[1:]:
            if item["url"] not in seen_urls:
                seen_urls.add(item["url"])
                merged.append(item)

        final_results = merged[:max_results]
        self.cache[q_norm] = (final_results, now + self.cache_ttl)
        return final_results
