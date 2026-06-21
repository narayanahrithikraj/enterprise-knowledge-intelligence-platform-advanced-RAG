import time
from typing import List, Dict, Any
import chromadb
from rank_bm25 import BM25Okapi
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from ..core.config import settings

class GeminiEmbeddingFunction:
    """High-speed custom wrapper class optimized for sub-5-second parallel execution windows."""
    def __init__(self, embeddings_engine: GoogleGenerativeAIEmbeddings):
        self.embeddings_engine = embeddings_engine

    def __call__(self, input: List[str]) -> List[List[float]]:
        results = []
        # UPGRADED: Expanded batch size to 100 to collapse loop iterations and network handshakes
        batch_size = 100 
        
        for i in range(0, len(input), batch_size):
            sub_batch = input[i:i+batch_size]
            
            # Progressive backoff retry loop - only executes if an exception is thrown
            for attempt in range(5):
                try:
                    batch_embeddings = self.embeddings_engine.embed_documents(sub_batch)
                    results.extend(batch_embeddings)
                    break 
                except Exception as e:
                    if "429" in str(e) and attempt < 4:
                        sleep_time = 5 * (attempt + 1)
                        print(f"⚠️ Rate Limit detected. Falling back to active safety pause for {sleep_time}s...")
                        time.sleep(sleep_time)
                    else:
                        raise e
            
            # REMOVED: The mandatory time.sleep(1) line from the happy path has been cut 
            # to unlock maximum bare-metal processing speeds.
            
        return results

class HybridRetrievalService:
    def __init__(self):
        # 1. Initialize Vector DB Client with Telemetry suppressed
        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=chromadb.config.Settings(anonymized_telemetry=False)
        )
        
        # 2. Configure Google Generative AI Embeddings Engine
        self.embeddings_engine = GoogleGenerativeAIEmbeddings(
            google_api_key=settings.GEMINI_API_KEY,
            model="models/gemini-embedding-001"
        )
        
        # 3. Instantiate Custom Call Mapping Signature
        chroma_embedding_fn = GeminiEmbeddingFunction(self.embeddings_engine)
        
        # 4. Initialize/Get Collection dedicated to Gemini Vectors
        self.collection = self.chroma_client.get_or_create_collection(
            name="enterprise_knowledge_gemini_v2",
            embedding_function=chroma_embedding_fn
        )
        
        # In-memory tracking for sparse BM25 engine
        self.bm25_corpus: List[str] = []
        self.bm25_metadata: List[Dict[str, Any]] = []
        self.bm25_engine: Any = None

    def add_documents(self, processed_chunks: List[Dict[str, Any]]):
        """Indexes child fragments into ChromaDB collection and calculates BM25 text footprints."""
        ids = []
        documents = []
        metadatas = []

        for item in processed_chunks:
            parent_text = item["parent_text"]
            
            for child in item["children"]:
                ids.append(child["child_id"])
                documents.append(child["text"])
                
                meta = child["metadata"].copy()
                meta["parent_text"] = parent_text
                metadatas.append(meta)

        if ids:
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            self.bm25_corpus.extend(documents)
            self.bm25_metadata.extend(metadatas)
            
            tokenized_corpus = [doc.lower().split(" ") for doc in self.bm25_corpus]
            self.bm25_engine = BM25Okapi(tokenized_corpus)

    def _reciprocal_rank_fusion(self, dense_results: List[Dict[str, Any]], sparse_results: List[Dict[str, Any]], k: int = 60) -> List[Dict[str, Any]]:
        """Applies Reciprocal Rank Fusion algorithm to unify dense and sparse metrics."""
        rrf_scores: Dict[str, Dict[str, Any]] = {}
        
        def apply_rrf(results: List[Dict[str, Any]]):
            for rank, item in enumerate(results, start=1):
                doc_id = item["id"]
                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = {"score": 0.0, "data": item}
                rrf_scores[doc_id]["score"] += 1.0 / (k + rank)

        apply_rrf(dense_results)
        apply_rrf(sparse_results)
        
        sorted_docs = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)
        return [item["data"] for item in sorted_docs]

    def hybrid_search(self, query: str, top_n: int = 3) -> List[Dict[str, Any]]:
        """Executes parallel semantic vector lookups and keyword text searches."""
        # --- 1. Dense (Vector) Search ---
        vector_res = self.collection.query(
            query_texts=[query],
            n_results=top_n * 2  
        )
        
        dense_hits = []
        if vector_res and vector_res["ids"] and vector_res["ids"][0]:
            for idx in range(len(vector_res["ids"][0])):
                dense_hits.append({
                    "id": vector_res["ids"][0][idx],
                    "text": vector_res["documents"][0][idx],
                    "metadata": vector_res["metadatas"][0][idx]
                })

        # --- 2. Sparse (BM25 Keyword) Search ---
        sparse_hits = []
        if self.bm25_engine:
            tokenized_query = query.lower().split(" ")
            scores = self.bm25_engine.get_scores(tokenized_query)
            top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_n * 2]
            
            for idx in top_indices:
                if scores[idx] > 0:  
                    sparse_hits.append({
                        "id": f"sparse_{idx}", 
                        "text": self.bm25_corpus[idx],
                        "metadata": self.bm25_metadata[idx]
                    })

        # --- 3. Fuse Results using RRF ---
        fused_results = self._reciprocal_rank_fusion(dense_hits, sparse_hits)
        return fused_results[:top_n]

# Singleton instantiation export pattern
hybrid_retrieval_service = HybridRetrievalService()