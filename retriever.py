from typing import List, Dict, Any
import chromadb
from rapidfuzz import fuzz


class HybridRetriever:
   

    def __init__(self, collection_name: str, index_path: str = ".data/index"):
       
        self.client = chromadb.PersistentClient(path=index_path)

        try:
            self.coll = self.client.get_collection(collection_name)
        except Exception:
            # If the collection doesn't exist, create it
            self.coll = self.client.create_collection(name=collection_name)

    def query(
        self,
        q: str,
        k: int = 6,
        dense_weight: float = 0.7,
        title_weight: float = 0.3
    ) -> List[Dict[str, Any]]:
       
        dense_results = self.coll.query(query_texts=[q], n_results=max(8, k))

        # Extract data safely
        ids = dense_results.get("ids", [[]])[0] if dense_results.get("ids") else []
        metadatas = dense_results.get("metadatas", [[]])[0] if dense_results.get("metadatas") else []
        documents = dense_results.get("documents", [[]])[0] if dense_results.get("documents") else []

        if not ids:
            return []  # No results found

        results = []
        for i, meta in enumerate(metadatas):
            result_item = dict(meta)
            result_item["doc"] = documents[i]
            result_item["_id"] = ids[i]
            result_item["_score_dense"] = 1.0 / (i + 1)
            result_item["_score_title"] = fuzz.partial_ratio(q, result_item.get("title", "")) / 100.0
            result_item["_score"] = (
                dense_weight * result_item["_score_dense"] +
                title_weight * result_item["_score_title"]
            )
            results.append(result_item)

        # Sort by hybrid score
        results.sort(key=lambda x: x["_score"], reverse=True)
        return results[:k]
