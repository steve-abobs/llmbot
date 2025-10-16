import json
import os
from typing import Any, Dict, List, Tuple

import faiss  # type: ignore
from sentence_transformers import SentenceTransformer


class FaissKB:
    def __init__(self, index_path: str, meta_path: str, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.index_path = index_path
        self.meta_path = meta_path
        os.makedirs(os.path.dirname(index_path), exist_ok=True)
        os.makedirs(os.path.dirname(meta_path), exist_ok=True)
        self.model = SentenceTransformer(model_name)
        self._load()

    def _load(self):
        if os.path.exists(self.index_path) and os.path.exists(self.meta_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "r", encoding="utf-8") as f:
                self.meta: List[Dict[str, Any]] = json.load(f)
        else:
            self.index = None
            self.meta = []

    def _save(self):
        if self.index is not None:
            faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, ensure_ascii=False, indent=2)

    def add_documents(self, docs: List[Dict[str, Any]]):
        # docs: [{"id": str, "title": str, "text": str}]
        texts = [d["text"] for d in docs]
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        if self.index is None:
            dim = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)
        self.meta.extend(docs)
        self._save()

    def query(self, text: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if self.index is None or len(self.meta) == 0:
            return []
        q = self.model.encode([text], convert_to_numpy=True, show_progress_bar=False)
        distances, indices = self.index.search(q, top_k)
        results: List[Dict[str, Any]] = []
        for i, idx in enumerate(indices[0]):
            if idx == -1 or idx >= len(self.meta):
                continue
            item = self.meta[idx]
            item = dict(item)
            item["score"] = float(distances[0][i])
            results.append(item)
        return results

# Convenience functions for simple usage

def add_documents(index_path: str, meta_path: str, docs: List[Dict[str, Any]]):
    kb = FaissKB(index_path, meta_path)
    kb.add_documents(docs)


def query(index_path: str, meta_path: str, text: str, top_k: int = 3) -> List[Dict[str, Any]]:
    kb = FaissKB(index_path, meta_path)
    return kb.query(text, top_k=top_k)
