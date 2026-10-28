import re
import urllib.parse
from urllib.parse import urlparse

class AIOverviewEngine:
    """
    Sovereign AI Overview Engine (Gemini-style Search Generative Synthesis).
    Generates structured, authoritative AI summaries, key takeaways, and source
    citations right at the top of search results without requiring external paid API keys.
    """
    def __init__(self):
        pass

    def _extract_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc.replace("www.", "")
        except Exception:
            return "web"

    def generate_overview(self, query: str, search_results: list = None, knowledge_panel: dict = None) -> dict:
        q_clean = query.strip()
        q_lower = q_clean.lower()
        search_results = search_results or []

        # 1. Sovereign Query: Er. Adam Eehan
        if any(k in q_lower for k in ["adam eehan", "adameehan", "adam", "eehan", "er. adam", "er adam"]):
            return {
                "title": "Aira AI Overview",
                "summary": (
                    "Er. Adam Eehan is an Indian systems architect, computer engineer, and the Founder & CEO of Aira Group of Technology. "
                    "He is the principal architect behind major sovereign computing initiatives, including Airlys OS (a 64-bit sovereign "
                    "desktop Linux operating system), AiraLang (a pure C native systems programming language with direct ELF binary emission), "
                    "and the sovereign Aira 3 Ultra AI engine."
                ),
                "bullets": [
                    "Founder & CEO of Aira Group of Technology, championing technological sovereignty and user freedom.",
                    "Architect of Airlys OS S1 Flagship Edition, featuring Linux Zen 6.x and KDE Plasma 6 desktop.",
                    "Creator of AiraLang S1 Duo, an ultra-fast pure C systems language with direct machine code generation.",
                    "Pioneer of sovereign, independent intelligence systems operating free from corporate telemetry."
                ],
                "sources": [
                    {"title": "adameehanairagroup (Er. Adam Eehan) · GitHub", "url": "https://github.com/adameehanairagroup", "domain": "github.com"},
                    {"title": "Aira Group of Technology", "url": "https://airagroup.technology", "domain": "airagroup.technology"},
                    {"title": "Adam Eehan — Professional Profile", "url": "https://in.linkedin.com/in/adam-eehan-1058133b7", "domain": "linkedin.com"}
                ]
            }

        # 2. Sovereign Query: Airlys OS
        if "airlys" in q_lower:
            return {
                "title": "Aira AI Overview",
                "summary": (
                    "Airlys OS S1 is an independent, 64-bit sovereign desktop operating system engineered by Er. Adam Eehan. "
                    "Built for modern hardware with direct UEFI boot architecture, it delivers exceptional performance "
                    "and responsiveness by combining a tuned Linux Zen 6.x kernel with a pristine KDE Plasma 6 desktop environment."
                ),
                "bullets": [
                    "Engineered by Er. Adam Eehan for absolute speed, stability, and developer sovereignty.",
                    "Powered by the Linux Zen 6.x performance kernel and Wayland-native KDE Plasma 6.",
                    "Features native integration of AiraLang S1 Duo (/usr/bin/airalang) as the primary systems language.",
                    "Guarantees total user freedom with zero corporate tracking, zero telemetry, and a clean desktop."
                ],
                "sources": [
                    {"title": "AirlysOS S1 Flagship Edition · GitHub", "url": "https://github.com/adameehanairagroup/AirlysOS", "domain": "github.com"},
                    {"title": "Aira Group Systems Architecture", "url": "https://airagroup.technology", "domain": "airagroup.technology"}
                ]
            }

        # 3. Sovereign Query: AiraLang
        if "airalang" in q_lower:
            return {
                "title": "Aira AI Overview",
                "summary": (
                    "AiraLang S1 Duo is a high-performance native systems programming language engineered by Er. Adam Eehan. "
                    "Written in pure C, it features a dual-mode execution architecture: a high-throughput bytecode interpreter "
                    "and a direct ELF64 machine-code emitter that compiles code into standalone static executables with zero external runtime dependencies."
                ),
                "bullets": [
                    "Direct ELF Machine Code Emitter (-b flag): generates standalone 64-bit binaries without external assemblers.",
                    "Pure C engine (s1duo): achieves ~35x speedup over legacy interpreters with sub-millisecond execution.",
                    "Complete systems standard library: built-in crypto (SHA-256), memory canary checks, network sockets, and AI modules.",
                    "Default systems language integrated natively into Airlys OS S1."
                ],
                "sources": [
                    {"title": "Airalang S1 Duo Engine · GitHub", "url": "https://github.com/adameehanairagroup/Airalang", "domain": "github.com"},
                    {"title": "Aira Group Language Documentation", "url": "https://airagroup.technology", "domain": "airagroup.technology"}
                ]
            }

        # 4. General Queries & Celebrities (Using Knowledge Panel & Search Results)
        summary_text = ""
        bullets = []
        sources = []

        if knowledge_panel and knowledge_panel.get("description"):
            desc = knowledge_panel["description"]
            summary_text = desc
            title = knowledge_panel.get("title", q_clean)
            subtitle = knowledge_panel.get("subtitle", "")
            
            # Formulate structured takeaways
            if subtitle:
                bullets.append(f"Entity: {title} — {subtitle}.")
            
            # Split description into sentences for key bullet highlights
            sentences = [s.strip() for s in re.split(r'\. |\.\n', desc) if len(s.strip()) > 15]
            for s in sentences[1:4]:
                bullets.append(s.rstrip(".") + ".")
            
            if knowledge_panel.get("links"):
                for name, link in knowledge_panel["links"][:2]:
                    sources.append({"title": f"{title} on {name}", "url": link, "domain": self._extract_domain(link)})

        # Augment with web results if needed
        for r in search_results:
            if len(sources) >= 3:
                break
            url = r.get("url", "")
            title = r.get("title", "")
            domain = self._extract_domain(url)
            if not any(s["url"] == url for s in sources):
                sources.append({"title": title, "url": url, "domain": domain})

            if not summary_text and r.get("snippet"):
                summary_text = r["snippet"]

        if not summary_text and search_results:
            top_snippet = search_results[0].get("snippet", "")
            summary_text = f"Overview for {q_clean}: {top_snippet}"

        if not bullets and search_results:
            for r in search_results[:3]:
                snip = r.get("snippet", "")
                if snip and len(snip) > 20:
                    bullets.append(snip[:140].rstrip(".") + "...")

        if not summary_text:
            return None

        return {
            "title": "Aira AI Overview",
            "summary": summary_text,
            "bullets": bullets[:3],
            "sources": sources[:3]
        }
