from rank_bm25 import BM25Okapi
import numpy as np

def compute_rrf(vector_results, keyword_results, k=60):
    """
    Applies Reciprocal Rank Fusion (RRF) to score and combine dense vector hits
    and sparse lexical keyword hits into a uniform, robust ranking hierarchy.
    """
    rrf_scores = {}
    
    # Secure utility to parse document text context across varying object models
    def get_doc_content(doc):
        if hasattr(doc, 'page_content'):
            return doc.page_content
        elif isinstance(doc, dict) and 'text' in doc:
            return doc['text']
        return str(doc)

    # Accumulate score metrics from dense vector operations
    for rank, doc in enumerate(vector_results):
        content_key = get_doc_content(doc)
        if content_key not in rrf_scores:
            rrf_scores[content_key] = {"doc": doc, "score": 0.0}
        rrf_scores[content_key]["score"] += 1.0 / (k + (rank + 1))
        
    # Accumulate score metrics from sparse keyword operations
    for rank, doc in enumerate(keyword_results):
        content_key = get_doc_content(doc)
        if content_key not in rrf_scores:
            rrf_scores[content_key] = {"doc": doc, "score": 0.0}
        rrf_scores[content_key]["score"] += 1.0 / (k + (rank + 1))
        
    # Sort and rank documents descending based on their merged RRF values
    fused_results = sorted(rrf_scores.values(), key=lambda x: x["score"], reverse=True)
    return [item["doc"] for item in fused_results]

def hybrid_retrieve(query: str, vector_db, all_documents, top_n=5):
    """
    Advanced RAG Node: Executes concurrent dense semantic and sparse lexical search queries,
    merging the results using Reciprocal Rank Fusion (RRF).
    
    :param query: The user string question.
    :param vector_db: Activated instance of your vector database (Chroma/FAISS).
    :param all_documents: The complete list of un-chunked document records from your database.
    :param top_n: Number of final optimal documents to return.
    """
    # Step 1: Execute Dense Semantic Query
    try:
        vector_hits = vector_db.similarity_search(query, k=10)
    except Exception:
        vector_hits = []

    # Step 2: Fallback to vector search if document repository metadata tracker is empty
    if not all_documents:
        return vector_hits[:top_n]
        
    # Standardize data inputs for the BM25 lexical engine
    raw_texts = []
    for doc in all_documents:
        if hasattr(doc, 'page_content'):
            raw_texts.append(doc.page_content)
        elif isinstance(doc, dict) and 'text' in doc:
            raw_texts.append(doc['text'])
        else:
            raw_texts.append(str(doc))

    # Tokenize corpus arrays
    tokenized_corpus = [text.lower().split() for text in raw_texts]
    bm25 = BM25Okapi(tokenized_corpus)
    
    # Tokenize and evaluate exact term matches
    tokenized_query = query.lower().split()
    doc_scores = bm25.get_scores(tokenized_query)
    
    # Isolate top sparse matches containing real overlapping keywords
    top_keyword_indices = np.argsort(doc_scores)[::-1][:10]
    keyword_hits = [all_documents[idx] for idx in top_keyword_indices if doc_scores[idx] > 0]
    
    # Step 3: Normalize and fuse rank matrix positions via RRF
    fused_docs = compute_rrf(vector_hits, keyword_hits, k=60)
    
    return fused_docs[:top_n]