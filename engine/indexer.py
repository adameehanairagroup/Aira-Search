import os
import re
import math
import json
import time
from collections import defaultdict, Counter

class InvertedIndex:
    def __init__(self, data_file=None):
        self.data_file = data_file
        # term -> list of [doc_id, frequency]
        self.index = defaultdict(list)
        # doc_id -> metadata dict
        self.documents = {}
        # doc_id -> total token count
        self.doc_lengths = {}
        self.total_docs = 0
        self.avg_doc_length = 0.0

        # BM25 Parameters
        self.k1 = 1.5
        self.b = 0.75

        # Stop words
        self.stop_words = {
            "a", "about", "an", "and", "are", "as", "at", "be", "by", "for", "from",
            "has", "he", "in", "is", "it", "its", "of", "on", "that", "the", "to",
            "was", "were", "will", "with"
        }

        if self.data_file and os.path.exists(self.data_file):
            self.load()

    def tokenize(self, text):
        if not text:
            return []
        text = text.lower()
        tokens = re.findall(r'[a-z0-9_\-\.\#\+]+', text)
        return [t for t in tokens if len(t) > 1 and t not in self.stop_words]

    def add_document(self, url, title, content, snippet=None):
        if not url:
            return None

        # Check if already indexed
        doc_id = None
        for did, dinfo in self.documents.items():
            if dinfo["url"] == url:
                doc_id = did
                break

        if doc_id is None:
            doc_id = len(self.documents) + 1

        tokens = self.tokenize(title + " " + content)
        doc_len = len(tokens)
        if doc_len == 0:
            doc_len = 1

        self.doc_lengths[doc_id] = doc_len
        tf_map = Counter(tokens)

        # Update inverted index
        for term, freq in tf_map.items():
            # Remove old entry if updating
            self.index[term] = [entry for entry in self.index[term] if entry[0] != doc_id]
            self.index[term].append([doc_id, freq])

        if not snippet:
            clean_content = re.sub(r'\s+', ' ', content).strip()
            snippet = clean_content[:200] + ("..." if len(clean_content) > 200 else "")

        self.documents[doc_id] = {
            "id": doc_id,
            "url": url,
            "title": title if title else url,
            "snippet": snippet,
            "indexed_at": time.time()
        }

        self.total_docs = len(self.documents)
        total_len = sum(self.doc_lengths.values())
        self.avg_doc_length = total_len / self.total_docs if self.total_docs > 0 else 0

        return doc_id

    def search(self, query, top_k=20):
        start_time = time.perf_counter()
        query_tokens = self.tokenize(query)

        if not query_tokens:
            return {"results": [], "total": 0, "time_ms": 0.0}

        scores = defaultdict(float)
        query_terms = set(query_tokens)

        for term in query_terms:
            if term not in self.index:
                continue

            postings = self.index[term]
            df = len(postings)
            # Inverse Document Frequency (IDF)
            idf = math.log(1.0 + (self.total_docs - df + 0.5) / (df + 0.5))

            for doc_id, tf in postings:
                doc_len = self.doc_lengths.get(doc_id, self.avg_doc_length)
                # BM25 Term Frequency weighting
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_length or 1.0)))
                bm25_term_score = idf * (numerator / denominator)

                # Bonus boost if term is in title
                title_lower = self.documents[doc_id]["title"].lower()
                if term in title_lower:
                    bm25_term_score *= 2.5

                scores[doc_id] += bm25_term_score

        # Exact phrase bonus
        clean_query = query.strip().lower()
        for doc_id in scores:
            doc = self.documents[doc_id]
            if clean_query in doc["title"].lower():
                scores[doc_id] += 5.0
            if clean_query in doc["snippet"].lower():
                scores[doc_id] += 2.0

        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for doc_id, score in ranked:
            doc = self.documents[doc_id].copy()
            doc["score"] = round(score, 3)
            results.append(doc)

        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        return {
            "query": query,
            "results": results,
            "total": len(scores),
            "time_ms": elapsed_ms
        }

    def save(self):
        if not self.data_file:
            return
        os.makedirs(os.path.dirname(os.path.abspath(self.data_file)), exist_ok=True)
        data = {
            "total_docs": self.total_docs,
            "avg_doc_length": self.avg_doc_length,
            "documents": self.documents,
            "doc_lengths": self.doc_lengths,
            "index": dict(self.index)
        }
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def load(self):
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.total_docs = data.get("total_docs", 0)
            self.avg_doc_length = data.get("avg_doc_length", 0.0)
            self.documents = {int(k): v for k, v in data.get("documents", {}).items()}
            self.doc_lengths = {int(k): v for k, v in data.get("doc_lengths", {}).items()}
            self.index = defaultdict(list, data.get("index", {}))
        except Exception as e:
            print(f"[!] Warning: Could not load index file: {e}")
