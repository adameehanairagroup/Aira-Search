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
    Sovereign Federated Web Retriever.
    Searches the real internet (independent websites, blogs, Vercel/Netlify apps,
    developer platforms, corporate portals, and verified documentation).
    Strictly filters out irrelevant Wikipedia noise so genuine web results shine!
    """
    def __init__(self, cache_ttl_seconds=900):
        self.cache = {}
        self.cache_ttl = cache_ttl_seconds
        self.browser_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
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

    def search_bing(self, query: str, max_results: int = 15):
        results = []
        url = f"https://www.bing.com/search?q={urllib.parse.quote(query)}&count=20"
        try:
            req = urllib.request.Request(url, headers=self.browser_headers)
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
                        "snippet": snippet or f"Visit {actual_url} for full details."
                    })
                    if len(results) >= max_results:
                        break
        except Exception:
            pass
        return results

    def search_github(self, query: str, max_results: int = 4):
        results = []
        q_clean = query.strip()
        # 1. Search Repositories
        try:
            url = f"https://api.github.com/search/repositories?q={urllib.parse.quote(q_clean)}&per_page={max_results}"
            req = urllib.request.Request(url, headers={"User-Agent": "AiraSearchBot/1.0"})
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                for it in data.get("items", []):
                    title = f"{it.get('full_name')} — GitHub"
                    desc = it.get("description") or f"Open source repository on GitHub."
                    stars = it.get("stargazers_count", 0)
                    lang = it.get("language") or "Code"
                    results.append({
                        "title": title,
                        "url": it.get("html_url"),
                        "snippet": f"{desc} ({lang} • ⭐ {stars} stars)"
                    })
        except Exception:
            pass

        # 2. Search Users (if query seems like a developer name)
        if any(w in q_clean.lower() for w in ["adam", "eehan", "developer", "creator", "author", "engineer"]):
            try:
                user_url = f"https://api.github.com/search/users?q={urllib.parse.quote(q_clean)}&per_page=2"
                req_u = urllib.request.Request(user_url, headers={"User-Agent": "AiraSearchBot/1.0"})
                with urllib.request.urlopen(req_u, timeout=4) as resp:
                    udata = json.loads(resp.read().decode("utf-8", errors="ignore"))
                    for u in udata.get("items", []):
                        results.append({
                            "title": f"{u.get('login')} (GitHub Developer Profile)",
                            "url": u.get("html_url"),
                            "snippet": f"Official GitHub developer profile for {u.get('login')}."
                        })
            except Exception:
                pass

        return results

    def search_wikipedia_strict(self, query: str):
        """
        Only returns Wikipedia if the article title is an EXACT or highly relevant match.
        Never injects random, loose, or unrelated Wikipedia articles!
        """
        results = []
        q_clean = query.strip().lower()
        try:
            url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(query)}&limit=1&namespace=0&format=json"
            req = urllib.request.Request(url, headers={"User-Agent": "AiraSearchBot/1.0 (+https://airagroup.technology)"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="ignore"))
                if data and len(data) > 3 and data[1]:
                    title = data[1][0]
                    snippet = data[2][0] if len(data[2]) > 0 else ""
                    page_url = data[3][0]

                    # Strict check: is query tightly related to the title?
                    t_lower = title.lower()
                    if q_clean in t_lower or t_lower in q_clean or all(w in t_lower for w in q_clean.split() if len(w) > 3):
                        results.append({
                            "title": f"{title} - Wikipedia",
                            "url": page_url,
                            "snippet": snippet or f"Read the full encyclopedia entry for {title} on Wikipedia."
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

        # Run independent fetchers in parallel
        t_bing = asyncio.to_thread(self.search_bing, query, 15)
        t_gh = asyncio.to_thread(self.search_github, query, 3)
        t_wiki = asyncio.to_thread(self.search_wikipedia_strict, query)

        res_bing, res_gh, res_wiki = await asyncio.gather(t_bing, t_gh, t_wiki)

        seen_urls = set()
        merged = []

        # 1. Real internet web pages (Bing index: self-hosted, blogs, Vercel/Netlify apps, company sites)
        for item in res_bing:
            url = item.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                merged.append(item)

        # 2. Real developer repositories & profiles from GitHub
        for item in res_gh:
            url = item.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                merged.append(item)

        # 3. Exactly matched Wikipedia entry (at most 1, placed at end or natural rank)
        for item in res_wiki:
            url = item.get("url")
            if url and url not in seen_urls:
                seen_urls.add(url)
                merged.append(item)

        final_results = merged[:max_results]
        self.cache[q_norm] = (final_results, now + self.cache_ttl)
        return final_results
