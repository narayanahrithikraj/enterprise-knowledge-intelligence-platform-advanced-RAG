from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph
from app.services.retrieval import hybrid_retrieval_service
from google.generativeai import GenerativeModel
from app.core.config import settings

# Explicit state schema declaration matching LangGraph compilation rules
class AgentState(TypedDict):
    question: str
    search_query: str
    documents: List[Dict[str, Any]]
    answer: str
    loop_count: int

knowledge_graph_builder = StateGraph(AgentState)

def retrieve_context_node(state: AgentState) -> Dict[str, Any]:
    query = state["question"]
    hits = hybrid_retrieval_service.hybrid_search(query=query, top_n=3)
    return {"documents": hits, "search_query": query}

def evaluate_and_generate_node(state: AgentState) -> Dict[str, Any]:
    question = state["question"]
    docs = state.get("documents", [])
    
    if not docs:
        return {"answer": "The active organization repository does not contain sufficient clear records to accurately validate a response to this query."}
        
    context_str = "\n\n".join([f"Source: {d['metadata']['source']}\nContent: {d['text']}" for d in docs])
    
    prompt = f"""You are an advanced Enterprise RAG Agent. Evaluate the provided corporate context records and answer the question precisely.
    If the context does not contain enough explicit facts to answer, explicitly output the fallback sentence: 'The active organization repository does not contain sufficient clear records to accurately validate a response to this query.'
    
    Context Records:
    {context_str}
    
    Question: {question}
    Answer:"""
    
    model = GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return {"answer": response.text}

# Register logical routing nodes
knowledge_graph_builder.add_node("retrieve_context", retrieve_context_node)
knowledge_graph_builder.add_node("evaluate_and_generate", evaluate_and_generate_node)

# FIXED: Using explicit configuration methods to make compilation stable across all versions
knowledge_graph_builder.set_entry_point("retrieve_context")
knowledge_graph_builder.add_edge("retrieve_context", "evaluate_and_generate")
knowledge_graph_builder.set_finish_point("evaluate_and_generate")

knowledge_graph = knowledge_graph_builder.compile()
print("🚀 LangGraph Agentic Engine Fully Compiled and Operational.")