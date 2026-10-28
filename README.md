# ⚡ Aira Search Engine

<p align="center">
  <strong style="font-size: 24px;">
    <span style="color: #4285f4;">A</span><span style="color: #ea4335;">i</span><span style="color: #fbbc05;">r</span><span style="color: #34a853;">a</span> Search
  </strong><br>
  <em>The World's Cleanest Sovereign Distributed Web Search Engine & Cluster Architecture</em><br>
  <strong>Architect & Founder:</strong> Er. Adam Eehan (Founder & CEO, Aira Group of Technology) 👑
</p>

<p align="center">
  <img src="https://img.shields.io/badge/UI-Google%20Clean%20Exact-4285F4?logo=google" alt="Google UI">
  <img src="https://img.shields.io/badge/Latency-%3C%205ms-brightgreen" alt="Latency">
  <img src="https://img.shields.io/badge/Algorithm-BM25%20Inverted%20Index-orange" alt="Algorithm">
  <img src="https://img.shields.io/badge/Deployment-Render%20Cloud%2024%2F7-blue" alt="Render">
  <img src="https://img.shields.io/badge/License-MIT-purple" alt="License">
</p>

---

## 🌟 Overview
**Aira Search** is a sovereign, ultra-fast distributed web search engine built from scratch to challenge commercial search monopolies with **zero tracking, zero bloat, and sub-10 millisecond retrieval speeds**.

It features an **exact Google-clean minimalist aesthetic**, powered by a high-throughput **asynchronous web crawler**, a mathematical **BM25 inverted index**, and a live REST API ready for 24/7 cloud deployment on **Render**.

---

## 🏛️ Core Architecture

```
[ Distributed Web Crawler ] ───▶ [ HTML Text Extractor ]
                                         │
                                         ▼
[ Clean Google UI ] ◀─── [ BM25 Inverted Index ] ◀─── [ Document Store ]
         │
         ▼
[ < 5ms Live Search Results ]
```

1. **🕷️ Asynchronous Web Spider (`engine/crawler.py`):**
   * Concurrent crawling with rate limiting and robots headers.
   * Extracts page titles, meta descriptions, headings, and discoverable outbound links.
2. **📚 BM25 Inverted Index Engine (`engine/indexer.py`):**
   * Pre-computed Inverse Document Frequency (IDF) and Term Frequency (TF) weights.
   * Title boost matching and exact phrase weighting.
   * Delivers ranked results in **under 5 milliseconds**!
3. **🎨 Google-Clean Frontend (`templates/`):**
   * Minimalist homepage with colorful Aira typography.
   * Fast, responsive search results page with breadcrumb URLs, blue titles, snippets, and pagination.
   * Seamless Light & Dark mode support.
4. **☁️ Render 24/7 Cloud Ready (`render.yaml` / `Dockerfile`):**
   * Pre-configured for Render's 100% free cloud tier with zero server maintenance.

---

## 🚀 Quick Local Run

1. **Clone repository:**
   ```bash
   git clone https://github.com/adameehanairagroup/Aira-Search.git
   cd Aira-Search
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Populate initial search index:**
   ```bash
   python data/populate_seeds.py
   ```

4. **Start Search Server:**
   ```bash
   python server.py
   ```
   * Open your browser at: `http://localhost:8080`

---

## ☁️ Deploy to Render (100% Free 24/7 Cloud)

1. Go to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** ➔ **Web Service**.
3. Connect your GitHub repository: `adameehanairagroup/Aira-Search`.
4. Render automatically detects `render.yaml` / Python settings:
   * **Build Command:** `pip install -r requirements.txt && python data/populate_seeds.py`
   * **Start Command:** `uvicorn server:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**!
6. Your live public search engine is ready at: `https://aira-search.onrender.com`! 🌐

---

## 📡 REST API Reference

### 1. Perform Search
```http
GET /api/search?q=Airlys+OS&limit=10
```
**Response:**
```json
{
  "query": "Airlys OS",
  "results": [
    {
      "id": 2,
      "url": "https://github.com/adameehanairagroup/AirlysOS",
      "title": "Airlys OS S1 — 64-Bit Sovereign Linux Operating System",
      "snippet": "Airlys OS S1 Flagship Edition engineered by Er. Adam Eehan...",
      "score": 8.45
    }
  ],
  "total": 1,
  "time_ms": 2.15
}
```

### 2. Crawl & Index New URL on Demand
```http
POST /api/crawl?url=https://example.com&max_pages=15
```

### 3. Cluster & Index Health
```http
GET /api/status
```

---

<p align="center">
  Engineered with ❤️ by <strong>Er. Adam Eehan</strong> (Founder & CEO, Aira Group of Technology)<br>
  <em>"Code the Higher Tomorrow"</em>
</p>
