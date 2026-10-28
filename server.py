import os
import sys
import time
from fastapi import FastAPI, Request, Query, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

# Setup paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from engine.indexer import InvertedIndex
from engine.crawler import WebSpider
from engine.web_retriever import WebRetriever

app = FastAPI(title="Aira Search Engine", version="1.1.0")

INDEX_FILE = os.path.join(BASE_DIR, "data", "index.json")
indexer = InvertedIndex(data_file=INDEX_FILE)
spider = WebSpider(indexer=indexer)
retriever = WebRetriever()

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Ensure static folder exists
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

START_TIME = time.time()

def render_template(template_name: str, request: Request, context: dict = None):
    if context is None:
        context = {}
    context["request"] = request
    try:
        # Modern Starlette (FastAPI >= 0.110.0 / Starlette >= 0.36.0)
        return templates.TemplateResponse(request=request, name=template_name, context=context)
    except TypeError:
        # Legacy Starlette signature
        return templates.TemplateResponse(template_name, context)

@app.api_route("/", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def home(request: Request):
    return render_template("index.html", request)

def auto_index_results(results: list):
    """Background task to index newly discovered web pages into local BM25 index."""
    changed = False
    for r in results:
        url = r.get("url")
        if url and not any(doc.get("url") == url for doc in indexer.documents.values()):
            indexer.add_document(
                url=url,
                title=r.get("title", ""),
                content=r.get("snippet", ""),
                snippet=r.get("snippet", "")
            )
            changed = True
    if changed:
        indexer.save()

@app.api_route("/search", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def search(request: Request, background_tasks: BackgroundTasks, q: str = Query("", alias="q")):
    q_clean = q.strip()
    if not q_clean:
        return render_template("index.html", request)

    start_t = time.perf_counter()

    # 1. Sovereign Local BM25 Index Search
    local_data = indexer.search(q_clean, top_k=15)
    local_results = local_data.get("results", [])

    sovereign_results = []
    for r in local_results:
        if r.get("score", 0) > 2.0 or any(k in q_clean.lower() for k in ["airlys", "aira", "adam", "eehan"]):
            r_copy = r.copy()
            r_copy["source"] = "Sovereign"
            sovereign_results.append(r_copy)

    # 2. Live Web Retrieval across Wikipedia, Bing, and GitHub
    web_results = await retriever.search_live(q_clean, max_results=15)

    # 3. Merge & Deduplicate
    seen_urls = set()
    combined = []

    for item in sovereign_results:
        url = item.get("url")
        if url not in seen_urls:
            seen_urls.add(url)
            combined.append(item)

    for item in web_results:
        url = item.get("url")
        if url not in seen_urls:
            seen_urls.add(url)
            combined.append(item)

    # Fallback to general local results if needed
    if len(combined) < 5:
        for item in local_results:
            url = item.get("url")
            if url not in seen_urls:
                seen_urls.add(url)
                combined.append(item)

    elapsed_ms = round((time.perf_counter() - start_t) * 1000, 1)

    # Auto-index web results in background
    if web_results:
        background_tasks.add_task(auto_index_results, web_results)

    return render_template("results.html", request, {
        "query": q_clean,
        "results": combined,
        "total": len(combined),
        "time_ms": elapsed_ms
    })

@app.api_route("/healthz", methods=["GET", "HEAD"])
async def healthz():
    return {"status": "ok", "service": "aira-search"}

@app.get("/api/search")
async def api_search(background_tasks: BackgroundTasks, q: str = Query(..., alias="q"), limit: int = 20):
    q_clean = q.strip()
    if not q_clean:
        return JSONResponse({"results": [], "total": 0, "time_ms": 0.0})

    start_t = time.perf_counter()
    local_data = indexer.search(q_clean, top_k=limit)
    web_results = await retriever.search_live(q_clean, max_results=limit)

    seen_urls = set()
    combined = []
    for item in local_data.get("results", []):
        if item.get("score", 0) > 2.0 or any(k in q_clean.lower() for k in ["airlys", "aira", "adam", "eehan"]):
            item_copy = item.copy()
            item_copy["source"] = "Sovereign"
            seen_urls.add(item["url"])
            combined.append(item_copy)

    for item in web_results:
        if item["url"] not in seen_urls:
            seen_urls.add(item["url"])
            combined.append(item)

    elapsed_ms = round((time.perf_counter() - start_t) * 1000, 1)
    if web_results:
        background_tasks.add_task(auto_index_results, web_results)

    return {
        "query": q_clean,
        "results": combined[:limit],
        "total": len(combined),
        "time_ms": elapsed_ms
    }

@app.get("/api/status")
async def api_status():
    uptime_sec = int(time.time() - START_TIME)
    return {
        "engine": "Aira Search Core v1.1 Hybrid",
        "cluster_status": "ONLINE",
        "federation": ["Wikipedia CirrusSearch", "Microsoft Bing Web Index", "GitHub Ecosystem", "Aira BM25 Core"],
        "total_documents_indexed": indexer.total_docs,
        "total_unique_terms": len(indexer.index),
        "avg_doc_length": round(indexer.avg_doc_length, 1),
        "uptime_seconds": uptime_sec,
        "architect": "Adam Eehan (Founder & CEO, Aira Group of Technology)"
    }

async def run_crawl_task(url: str, max_pages: int):
    print(f"[*] Starting crawl job for seed: {url}")
    await spider.crawl_seeds([url], max_pages=max_pages)
    print(f"[✓] Crawl finished. Total documents in index: {indexer.total_docs}")

@app.post("/api/crawl")
async def api_crawl(background_tasks: BackgroundTasks, url: str = Query(..., alias="url"), max_pages: int = 10):
    background_tasks.add_task(run_crawl_task, url, max_pages)
    return {
        "status": "CRAWL_QUEUED",
        "target_url": url,
        "max_pages": max_pages,
        "message": "Background web spider dispatched. Index will update automatically."
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
