import os
import json
import urllib.request
import urllib.parse
from urllib.parse import urlparse
import re

class AIOverviewEngine:
    """
    Sovereign AI Overview Engine (Gemini-powered Search Generative Synthesis).
    Provides comprehensive, detailed web search syntheses and intelligent interactive chat.
    Default language is strictly English, with dynamic language adaptation based on user input.
    """
    def __init__(self):
        self.cache = {}
        self.model_name = "gemini-2.5-flash"

    def _get_api_key(self) -> str:
        for env_k in ["GEMINI_API_KEY", "AIRA_AI_KEY", "GOOGLE_API_KEY"]:
            val = os.environ.get(env_k)
            if val and val.strip():
                return val.strip()

        try:
            cfg_path = os.path.expanduser("~/.config/airalang/config.json")
            if os.path.exists(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    k = data.get("keys", {}).get("gemini")
                    if k and k.strip():
                        return k.strip()
        except Exception:
            pass

        return "AIzaSyBiFtmDWFD3ln8uNkGYhqRTVbRSh85b8vA"

    def _call_gemini(self, prompt: str, system_instruction: str = "", timeout: int = 15) -> str:
        key = self._get_api_key()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        if system_instruction:
            payload["system_instruction"] = {"parts": [{"text": system_instruction}]}

        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        
        for attempt in range(2):
            try:
                with urllib.request.urlopen(req, timeout=timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "").strip()
            except Exception as e:
                if attempt == 1:
                    print(f"[Aira AI] Endpoint call warning: {e}")
        return ""

    def _extract_domain(self, url: str) -> str:
        try:
            return urlparse(url).netloc.replace("www.", "")
        except Exception:
            return "web"

    def generate_overview(self, query: str, search_results: list = None, knowledge_panel: dict = None) -> dict:
        q_clean = query.strip()
        q_lower = q_clean.lower()
        search_results = search_results or []

        if q_lower in self.cache:
            return self.cache[q_lower]

        # Gather real web sources
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

        # Build context from web search & knowledge graph
        context_lines = []
        if knowledge_panel:
            context_lines.append(f"Entity: {knowledge_panel.get('title')} ({knowledge_panel.get('subtitle', '')})")
            if knowledge_panel.get("description"):
                context_lines.append(f"Description: {knowledge_panel.get('description')}")
            for k, v in knowledge_panel.get("attributes", []):
                context_lines.append(f"{k}: {v}")

        for r in search_results[:8]:
            snip = r.get("snippet", "")
            if snip:
                context_lines.append(f"- {r.get('title')}: {snip}")

        context_text = "\n".join(context_lines)

        # Prompt for English Overview synthesis (Detailed, comprehensive, neutral)
        sys_inst = (
            "You are AIRA Search Generative Engine. "
            "Your task is to synthesize the web search results into an authoritative, detailed, and comprehensive AI Overview (Google SGE / Gemini style). "
            "DEFAULT LANGUAGE: You MUST write the overview strictly in ENGLISH.\n"
            "Style: Objective, informative, fact-based, rich, and well-structured. Do NOT output promotional slogans or bias. "
            "Format your response strictly as:\n"
            "SUMMARY: <A thorough, comprehensive overview paragraph explaining the subject with depth (3 to 4 sentences)>\n"
            "BULLETS:\n"
            "- <Detailed key highlight or factual finding 1>\n"
            "- <Detailed key highlight or factual finding 2>\n"
            "- <Detailed key highlight or factual finding 3>\n"
            "- <Detailed key highlight or factual finding 4>\n"
            "No preface, no disclaimers."
        )

        prompt = f"Search Query: {q_clean}\n\nWeb Search & Knowledge Graph Context:\n{context_text}"
        ai_resp = self._call_gemini(prompt, system_instruction=sys_inst, timeout=6)

        summary_text = ""
        bullets = []

        if ai_resp:
            m_sum = re.search(r"SUMMARY:\s*(.*?)(?=\nBULLETS:|\n\n|$)", ai_resp, re.DOTALL)
            summary_text = m_sum.group(1).strip() if m_sum else ai_resp.split("\n")[0]
            bullets = [b.lstrip("-*• ").strip() for b in ai_resp.split("BULLETS:")[-1].split("\n") if b.strip().startswith(("-", "*", "•"))]

        # Graceful fallback if offline
        if not summary_text:
            if knowledge_panel and knowledge_panel.get("description"):
                summary_text = knowledge_panel["description"]
                sentences = [s.strip() for s in re.split(r'\. |\.\n', summary_text) if len(s.strip()) > 15]
                bullets = [s.rstrip(".") + "." for s in sentences[1:5]]
            elif search_results:
                summary_text = search_results[0].get("snippet", f"Search results for {q_clean}.")
                for r in search_results[:4]:
                    s = r.get("snippet", "")
                    if s:
                        bullets.append(s[:160].rstrip(".") + "...")

        if not summary_text:
            return None

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
        Interactive follow-up chat.
        Dynamically detects user language:
        - If user asks in Manglish/Malayalam, replies in natural Manglish.
        - If user asks in English, replies in English.
        - Delivers detailed, comprehensive replies based on the real web findings and knowledge.
        - Neutral and factual, no forced corporate loyalty slogans.
        """
        sys_inst = (
            "You are AIRA, an intelligent AI search assistant integrated into Aira Search.\n\n"
            "LANGUAGE DETECTION RULE:\n"
            "1. Analyze the user prompt's language:\n"
            "   - If the user writes in Malayalam or Manglish (e.g. 'aaranu', 'enthaanu', 'parayamo', 'nook', 'njan'), reply naturally in clear, friendly Manglish (Malayalam in English alphabet). NEVER use Malayalam script (മലയാളം ലിപി വേണ്ട, strictly Manglish).\n"
            "   - If the user writes in English, reply in fluent, professional English.\n"
            "   - Match whatever language the user initiates.\n"
            "2. RESPONSE DEPTH: Give comprehensive, detailed, informative answers ('valiya replays') incorporating facts from the search topic, internet sources, and world knowledge.\n"
            "3. OBJECTIVITY & TONE: Maintain a helpful, intelligent, objective tone. Do not inject forced company loyalty slogans or artificial praise into search results.\n"
            "4. KNOWN FACTS ABOUT ER. ADAM EEHAN: If asked about Er. Adam Eehan, he is an Indian Software Engineer, AI Architect & AI Engineer, and Founder of Aira Group of Technology (Wikidata: Q141755677, website: https://adameehan.vercel.app), creator of Airlys OS and AiraLang.\n"
            "5. NO corporate disclaimers or repetitive boilerplates."
        )

        prompt = f"Topic context: {query}\nUser question: {user_prompt}\nAira:"
        answer = self._call_gemini(prompt, system_instruction=sys_inst, timeout=9)

        if not answer:
            return (
                f"I have summarized the available web results for \"{query}\". "
                f"Please try asking your question again."
            )

        return answer
