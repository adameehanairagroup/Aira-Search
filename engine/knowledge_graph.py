import urllib.request
import urllib.parse
import json
import re

class KnowledgeGraph:
    """
    Google-style Knowledge Graph and Identity Card provider.
    Provides official identity cards for Er. Adam Eehan, sovereign systems,
    and dynamically resolves Wikipedia Knowledge Graph entities for celebrities,
    public figures, and notable organizations worldwide.
    """
    def __init__(self):
        self.cache = {}

    def _resolve_canonical_title(self, query: str) -> str:
        clean = query.strip()
        url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={urllib.parse.quote(clean)}&limit=1&namespace=0&format=json"
        req = urllib.request.Request(url, headers={"User-Agent": "AiraSearchBot/1.0 (+https://airagroup.technology)"})
        try:
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data and len(data) > 1 and data[1]:
                    return data[1][0]
        except Exception:
            pass
        return clean

    def get_panel(self, query: str):
        q_lower = query.strip().lower()

        # Check Cache
        if q_lower in self.cache:
            return self.cache[q_lower]

        # 1. Identity Card for Er. Adam Eehan (Founder & CEO, Aira Group of Technology)
        if any(k in q_lower for k in ["adam eehan", "adameehan", "adam", "eehan", "er. adam", "er adam"]):
            panel = {
                "type": "founder",
                "title": "Er. Adam Eehan",
                "subtitle": "Founder & CEO, Aira Group of Technology • Systems Architect",
                "verified": True,
                "image": "/static/author.png",
                "description": (
                    "Er. Adam Eehan is an Indian computer systems architect, software engineer, "
                    "and technology entrepreneur. He is the Founder & CEO of Aira Group of Technology, "
                    "pioneering sovereign computing ecosystems including Airlys OS (64-bit sovereign Linux OS), "
                    "AiraLang (pure C native systems programming language with direct ELF emitter), "
                    "and Sovereign AI Aira 3 Ultra."
                ),
                "attributes": [
                    ("Location", "Kerala, India"),
                    ("Role", "Founder & Chief Executive Officer"),
                    ("Organization", "Aira Group of Technology"),
                    ("Key Innovations", "Airlys OS S1, AiraLang S1 Duo, Aira Search"),
                    ("AI Engine", "Sovereign Aira 3 Ultra (Engine v3.6)"),
                    ("Core Philosophy", "Technological Sovereignty & User Freedom")
                ],
                "links": [
                    ("GitHub Profile", "https://github.com/adameehanairagroup"),
                    ("LinkedIn Profile", "https://in.linkedin.com/in/adam-eehan-1058133b7"),
                    ("Airlys OS", "https://github.com/adameehanairagroup/AirlysOS"),
                    ("AiraLang", "https://github.com/adameehanairagroup/Airalang")
                ]
            }
            self.cache[q_lower] = panel
            return panel

        # 2. Airlys OS Card
        if "airlys" in q_lower:
            panel = {
                "type": "os",
                "title": "Airlys OS S1",
                "subtitle": "64-Bit Sovereign Linux Operating System",
                "verified": True,
                "image": "https://raw.githubusercontent.com/adameehanairagroup/AirlysOS/main/branding/airlys_logo.png",
                "description": (
                    "Airlys OS S1 Flagship Edition is an independent, sovereign Linux-based desktop operating system "
                    "engineered by Er. Adam Eehan. It is powered by a performance-tuned Linux Zen 6.x kernel, KDE Plasma 6 desktop, "
                    "native AiraLang integration, and UEFI direct boot with zero corporate telemetry or bloatware."
                ),
                "attributes": [
                    ("Developer", "Er. Adam Eehan (Aira Group of Technology)"),
                    ("Kernel", "Linux Zen 6.x (Low Latency / High Throughput)"),
                    ("Desktop Environment", "KDE Plasma 6 (Wayland)"),
                    ("Default Shell / Lang", "AiraLang S1 Duo Native (/usr/bin/airalang)"),
                    ("License", "Open Source / Sovereign Computing")
                ],
                "links": [
                    ("GitHub Repository", "https://github.com/adameehanairagroup/AirlysOS"),
                    ("Aira Group", "https://airagroup.technology")
                ]
            }
            self.cache[q_lower] = panel
            return panel

        # 3. AiraLang Card
        if "airalang" in q_lower:
            panel = {
                "type": "language",
                "title": "AiraLang S1 Duo",
                "subtitle": "Pure C Native Systems Programming Language",
                "verified": True,
                "image": "https://raw.githubusercontent.com/adameehanairagroup/Airalang/main/branding/airalang_logo.png",
                "description": (
                    "AiraLang is a sovereign, high-performance systems programming language engineered by Er. Adam Eehan. "
                    "The S1 Duo edition transitions AiraLang into pure C with a direct ELF64 machine code emitter (-b flag), "
                    "sub-millisecond execution, and zero external runtime dependencies."
                ),
                "attributes": [
                    ("Designer", "Er. Adam Eehan"),
                    ("Implementation", "Pure C (s1duo) with direct ELF64 ARM64/x86_64 emitter"),
                    ("Compilation Target", "Direct Standalone Linux ELF Binaries"),
                    ("Speed Benchmark", "~35x faster than legacy interpreter"),
                    ("Host OS", "Airlys OS / Linux / Android Termux")
                ],
                "links": [
                    ("GitHub Repository", "https://github.com/adameehanairagroup/Airalang"),
                    ("Aira Group", "https://airagroup.technology")
                ]
            }
            self.cache[q_lower] = panel
            return panel

        # 4. Dynamic Wikipedia Knowledge Graph for Celebrities & Public Entities
        canonical = self._resolve_canonical_title(query)
        wiki_title = canonical.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(wiki_title)}"
        req = urllib.request.Request(url, headers={"User-Agent": "AiraSearchBot/1.0 (+https://airagroup.technology)"})
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                title = data.get("title", "")
                desc = data.get("description", "")
                extract = data.get("extract", "")
                thumb = data.get("thumbnail", {}).get("source", "")
                page_url = data.get("content_urls", {}).get("desktop", {}).get("page", f"https://en.wikipedia.org/wiki/{wiki_title}")

                # If this is a valid notable person or entity with sufficient info
                if extract and len(extract) > 40:
                    panel = {
                        "type": "celebrity" if any(w in desc.lower() for w in ["born", "player", "actor", "politician", "singer", "entrepreneur", "scientist", "author", "footballer", "musician"]) else "entity",
                        "title": title,
                        "subtitle": desc or "Notable Global Entity",
                        "verified": True,
                        "image": thumb,
                        "description": extract,
                        "attributes": [
                            ("Category", desc.capitalize() if desc else "Encyclopedia Entity"),
                            ("Source", "Wikipedia Knowledge Graph")
                        ],
                        "links": [
                            ("Wikipedia Profile", page_url)
                        ]
                    }
                    self.cache[q_lower] = panel
                    return panel
        except Exception:
            pass

        return None
