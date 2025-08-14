from typing import List, Dict, Any
import chromadb
from rapidfuzz import fuzz


class HybridRetriever:
    """
    A retriever that combines dense vector search results from ChromaDB
    with a fuzzy title matching score to produce a hybrid ranking.
    """

    def __init__(self, collection_name: str, index_path: str = ".data/index"):
        """
        Initialize the retriever with a ChromaDB persistent collection.

        Args:
            collection_name (str): Name of the collection in ChromaDB.
            index_path (str): Path where ChromaDB will store index data.
        """
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
        """
        Perform a hybrid search.

        Args:
            q (str): The query string.
            k (int): Number of results to return.
            dense_weight (float): Weight for dense embedding score.
            title_weight (float): Weight for fuzzy title score.

        Returns:
            List[Dict[str, Any]]: A list of search result metadata with scores.
        """
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
