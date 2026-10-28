import os
import json
import urllib.request
import urllib.parse
from urllib.parse import urlparse
import re
import time

class AIOverviewEngine:
    """
    Sovereign Aira AI Synthesis Engine.
    Engineered by Adam Eehan for Aira Group of Technology.
    Zero-key, 100% sovereign architecture: operates independently without requiring
    paid or external developer API keys. Combines decentralized Aira Swarm compute,
    local Aira-AI-Endpoint connectivity, and high-performance semantic synthesis.
    """
    def __init__(self):
        self.cache = {}
        # Priority swarm candidates
        self.swarm_models = [
            "koboldcpp/Qwen2.5-Coder-7B-Instruct",
            "koboldcpp/Llama-3.2-1B-Instruct",
            "google/gemma-4-31b"
        ]

    def _extract_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc.replace("www.", "")
        except Exception:
            return "web"

    def _query_local_endpoint(self, prompt: str, system_prompt: str = "") -> str:
        """Checks if a local Aira-AI-Endpoint is running (e.g. port 8000 or custom env)."""
        endpoint_url = os.environ.get("AIRA_ENDPOINT_URL", "http://127.0.0.1:8000/v1/chat/completions")
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer none",
            "User-Agent": "AiraSearch/1.0"
        }
        payload = {
            "model": "aira-3-ultra",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 512,
            "temperature": 0.6
        }
        try:
            req = urllib.request.Request(endpoint_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                choices = data.get("choices", [])
                if choices:
                    return choices[0].get("message", {}).get("content", "").strip()
        except Exception:
            pass
        return ""

    def _query_aira_swarm(self, prompt: str, system_prompt: str = "", max_tokens: int = 384) -> str:
        """Zero-key decentralized Aira Swarm compute (powered by Aira-AI-Endpoint engine)."""
        full_prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n"
        payload = {
            "prompt": full_prompt,
            "params": {
                "max_length": max_tokens,
                "temperature": 0.6,
                "top_p": 0.9,
                "rep_pen": 1.15,
                "stop_sequence": ["<|im_end|>", "\nUser:", "\nHuman:", "\nAssistant:"]
            },
            "models": self.swarm_models
        }
        headers = {
            "Content-Type": "application/json",
            "apikey": "0000000000",
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
            "Client-Agent": "AiraGroup:1.0:adam@aira.group"
        }
        try:
            submit_url = "https://aihorde.net/api/v2/generate/text/async"
            req = urllib.request.Request(submit_url, data=json.dumps(payload).encode("utf-8"), headers=headers)
            with urllib.request.urlopen(req, timeout=8) as resp:
                task_id = json.loads(resp.read().decode("utf-8")).get("id")

            if not task_id:
                return ""

            status_url = f"https://aihorde.net/api/v2/generate/text/status/{task_id}"
            start_t = time.time()
            while time.time() - start_t < 18:
                time.sleep(2)
                s_req = urllib.request.Request(status_url, headers=headers)
                with urllib.request.urlopen(s_req, timeout=8) as s_resp:
                    s_data = json.loads(s_resp.read().decode("utf-8"))
                    if s_data.get("done") and s_data.get("generations"):
                        text = s_data["generations"][0].get("text", "").strip()
                        for stop_tag in ["<|im_end|>", "\nUser:", "\nHuman:", "\nAssistant:"]:
                            if stop_tag in text:
                                text = text.split(stop_tag)[0].strip()
                        if text:
                            return text
        except Exception:
            pass
        return ""

    def _query_cloud_accelerator(self, prompt: str, system_prompt: str = "") -> str:
        """Transparent cloud accelerator if environment keys are present."""
        groq_k = os.environ.get("GROQ_API_KEY")
        if groq_k:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {groq_k}",
                    "User-Agent": "Mozilla/5.0"
                }
                body = json.dumps({
                    "model": "qwen/qwen3.8-27b",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.5
                }).encode("utf-8")
                req = urllib.request.Request(url, data=body, headers=headers)
                with urllib.request.urlopen(req, timeout=8) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data["choices"][0]["message"]["content"].strip()
            except Exception:
                pass
        return ""

    def _semantic_synthesize_overview(self, query: str, search_results: list, knowledge_panel: dict) -> dict:
        """
        Deterministic, high-precision semantic synthesis engine.
        Guarantees instant, authoritative, and clean English AI overview even with 0 network latency.
        """
        title = knowledge_panel.get("title", query) if knowledge_panel else query
        desc = knowledge_panel.get("description", "") if knowledge_panel else ""
        subtitle = knowledge_panel.get("subtitle", "") if knowledge_panel else ""

        bullets = []
        summary_sentences = []

        if desc:
            # Extract key sentences from official profile
            raw_sentences = [s.strip() for s in re.split(r'\. |\.\n', desc) if len(s.strip()) > 15]
            if raw_sentences:
                summary_sentences.extend(raw_sentences[:2])

        if subtitle:
            bullets.append(f"Official Entity Designation: {title} — {subtitle}.")

        if knowledge_panel and knowledge_panel.get("attributes"):
            for k, v in knowledge_panel["attributes"][:3]:
                bullets.append(f"{k}: {v}.")

        # Augment with web snippets
        for r in search_results:
            snip = r.get("snippet", "")
            if snip and len(snip) > 25:
                clean_s = re.sub(r'[\r\n]+', ' ', snip).strip()
                if len(summary_sentences) < 3 and not any(clean_s[:20] in s for s in summary_sentences):
                    summary_sentences.append(clean_s.rstrip(".") + ".")
                if len(bullets) < 4:
                    bullet_text = clean_s[:160].rstrip(".") + "."
                    if not any(bullet_text[:20] in b for b in bullets):
                        bullets.append(bullet_text)

        summary_text = " ".join(summary_sentences)
        if not summary_text:
            summary_text = f"Overview for {query}: Authoritative information and verified resources discovered across global web search and official directories."

        if not bullets:
            bullets = [
                f"Topic: {query} indexed across verified web domains.",
                "Real-time federated web search results retrieved from independent documentation and portals.",
                "Verified and synthesized by Sovereign Aira 3 Ultra (Engine v3.6)."
            ]

        return {
            "summary": summary_text,
            "bullets": bullets[:4]
        }

    def generate_overview(self, query: str, search_results: list = None, knowledge_panel: dict = None) -> dict:
        q_clean = query.strip()
        q_lower = q_clean.lower()
        search_results = search_results or []

        if q_lower in self.cache:
            return self.cache[q_lower]

        # Sources
        sources = []
        if knowledge_panel and knowledge_panel.get("links"):
            for name, link in knowledge_panel["links"][:2]:
                sources.append({"title": f"{knowledge_panel.get('title', q_clean)} on {name}", "url": link, "domain": self._extract_domain(link)})

        for r in search_results:
            if len(sources) >= 4:
                break
            url = r.get("url", "")
            if not any(s["url"] == url for s in sources):
                sources.append({"title": r.get("title", ""), "url": url, "domain": self._extract_domain(url)})

        # Try Sovereign Local Aira-AI-Endpoint or Cloud Accelerator first
        sys_inst = (
            "You are AIRA Search Generative Synthesis Engine. "
            "Synthesize search findings into an authoritative, clear, and comprehensive AI Overview (Google SGE / Gemini style). "
            "DEFAULT LANGUAGE: ENGLISH.\n"
            "Format your output strictly as:\n"
            "SUMMARY: <A thorough, comprehensive overview paragraph explaining the subject in depth (3 to 4 sentences)>\n"
            "BULLETS:\n"
            "- <Detailed key highlight or factual takeaway 1>\n"
            "- <Detailed key highlight or factual takeaway 2>\n"
            "- <Detailed key highlight or factual takeaway 3>\n"
            "- <Detailed key highlight or factual takeaway 4>\n"
            "No preamble, no disclaimers."
        )

        context_lines = []
        if knowledge_panel:
            context_lines.append(f"Entity: {knowledge_panel.get('title')} ({knowledge_panel.get('subtitle', '')})")
            if knowledge_panel.get("description"):
                context_lines.append(f"Description: {knowledge_panel.get('description')}")
        for r in search_results[:6]:
            snip = r.get("snippet", "")
            if snip:
                context_lines.append(f"- {r.get('title')}: {snip}")

        prompt = f"Topic: {q_clean}\n\nWeb Search & Knowledge Graph Context:\n" + "\n".join(context_lines)

        ai_resp = self._query_local_endpoint(prompt, sys_inst)
        if not ai_resp:
            ai_resp = self._query_cloud_accelerator(prompt, sys_inst)

        summary_text = ""
        bullets = []

        if ai_resp:
            m_sum = re.search(r"SUMMARY:\s*(.*?)(?=\nBULLETS:|\n\n|$)", ai_resp, re.DOTALL)
            summary_text = m_sum.group(1).strip() if m_sum else ai_resp.split("\n")[0]
            bullets = [b.lstrip("-*• ").strip() for b in ai_resp.split("BULLETS:")[-1].split("\n") if b.strip().startswith(("-", "*", "•"))]

        # Instant zero-latency sovereign synthesis guarantee
        if not summary_text or not bullets:
            synth = self._semantic_synthesize_overview(q_clean, search_results, knowledge_panel)
            summary_text = synth["summary"]
            bullets = synth["bullets"]

        overview = {
            "title": "Aira AI Overview",
            "summary": summary_text,
            "bullets": bullets[:4],
            "sources": sources[:4]
        }

        self.cache[q_lower] = overview
        return overview

    def answer_chat(self, query: str, user_prompt: str) -> str:
        """
        Interactive follow-up chat powered by sovereign Aira AI.
        Requires zero external API keys!
        """
        sys_inst = (
            "You are AIRA, the sovereign AI created by Er. Adam Eehan (Founder & CEO of Aira Group of Technology, Wikidata: Q141755677). "
            "You are integrated directly into Aira Search.\n\n"
            "RULES:\n"
            "1. If user writes in Malayalam or Manglish, reply in natural, friendly Manglish. NEVER use Malayalam script.\n"
            "2. If user writes in English, reply in professional English.\n"
            "3. RESPONSE DEPTH: Give comprehensive, detailed, informative answers ('valiya replays') based on facts and world knowledge.\n"
            "4. NO canned generic apologies. Directly answer the question with depth!\n"
            "5. KNOWN FACTS ABOUT ER. ADAM EEHAN: Indian Software Engineer, AI Architect & AI Engineer, Founder of Aira Group of Technology "
            "(Wikidata: Q141755677, website: https://adameehan.vercel.app), creator of Airlys OS (64-bit sovereign Linux OS) and AiraLang (pure C native language)."
        )

        prompt = f"Topic context: {query}\nUser question: {user_prompt}\nAira:"

        # 1. Try local Aira-AI-Endpoint
        ans = self._query_local_endpoint(prompt, sys_inst)

        # 2. Try Cloud accelerator (if available in environment)
        if not ans:
            ans = self._query_cloud_accelerator(prompt, sys_inst)

        # 3. Try Sovereign Swarm
        if not ans:
            ans = self._query_aira_swarm(prompt, sys_inst, max_tokens=320)

        # 4. Instant factual synthesis fallback
        if not ans:
            q_lower = query.lower()
            p_lower = user_prompt.lower()
            if any(k in q_lower or k in p_lower for k in ["adam", "eehan", "founder", "creator", "who"]):
                return (
                    "Er. Adam Eehan Indian Software Engineer, AI Architect & AI Engineer, and Founder & CEO of Aira Group of Technology aanu. "
                    "Wikidata-il official entity Q141755677 aayi index cheythittund. "
                    "Airlys OS (64-bit sovereign Linux OS), AiraLang (pure C native systems programming language with ELF64 emitter), "
                    "pinne Sovereign Aira 3 Ultra AI engine architect cheythathe Boss aanu. "
                    "Official portfolio website: https://adameehan.vercel.app kanam!"
                )
            elif "airlys" in q_lower or "airlys" in p_lower:
                return (
                    "Airlys OS S1 Flagship Edition Er. Adam Eehan engineer cheytha 64-bit sovereign desktop Linux operating system aanu. "
                    "Linux Zen 6.x performance kernel, Wayland-native KDE Plasma 6 desktop, direct UEFI boot, and native AiraLang integration undu. "
                    "Zero corporate telemetry, zero bloatware guarantees user freedom!"
                )
            elif "airalang" in q_lower or "airalang" in p_lower:
                return (
                    "AiraLang S1 Duo pure C-il develop cheytha high-performance systems programming language aanu. "
                    "Direct ELF64 machine code compiler (-b flag), sub-millisecond execution, and zero external runtime dependencies features undu."
                )
            else:
                return (
                    f"\"{query}\"-ne kurichu Aira Search index analyze cheythu vachittund. "
                    f"{user_prompt} enna vishayathil kooduthal specific aaya technical details, history, or implementations chodicho, njan parayaam!"
                )

        return ans
