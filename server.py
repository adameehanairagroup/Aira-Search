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

app = FastAPI(title="Aira Search Engine", version="1.0.0")

INDEX_FILE = os.path.join(BASE_DIR, "data", "index.json")
indexer = InvertedIndex(data_file=INDEX_FILE)
spider = WebSpider(indexer=indexer)

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

@app.api_route("/search", methods=["GET", "HEAD"], response_class=HTMLResponse)
async def search(request: Request, q: str = Query("", alias="q")):
    q_clean = q.strip()
    if not q_clean:
        return render_template("index.html", request)

    search_data = indexer.search(q_clean, top_k=25)
    return render_template("results.html", request, {
        "query": q_clean,
        "results": search_data["results"],
        "total": search_data["total"],
        "time_ms": search_data["time_ms"]
    })

@app.api_route("/healthz", methods=["GET", "HEAD"])
async def healthz():
    return {"status": "ok", "service": "aira-search"}

@app.get("/api/search")
async def api_search(q: str = Query(..., alias="q"), limit: int = 20):
    if not q.strip():
        return JSONResponse({"results": [], "total": 0, "time_ms": 0.0})
    return indexer.search(q.strip(), top_k=limit)

@app.get("/api/status")
async def api_status():
    uptime_sec = int(time.time() - START_TIME)
    return {
        "engine": "Aira Search Core v1.0",
        "cluster_status": "ONLINE",
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
