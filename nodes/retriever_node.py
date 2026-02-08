import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from agent_state import AgentState
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from llm_node import llm
load_dotenv()

# Initialize embeddings globally to prevent re-loading on every call
local_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def retriever(state: AgentState):

    print("-----RAG RETRIVER ACTIVATED NODE-----")
    """
    
    Advanced RAG Node: Performs semantic search with relevance filtering 
    and document formatting for high-reasoning LLMs.
    """
    subject = state.get('subject', 'No Subject')
    email_body = state.get('raw_email', '')
    
    
    # print(f"🔍 [RAG] Initiating retrieval for: {subject}")
    # print(f"retiever actived to retriveed the dat for the query {email_body}")

    # 1. Initialize Vector Store connection
    vector_store = Chroma(
        persist_directory="./knowledge_base",
        embedding_function=local_embeddings,
        collection_name="corporate_knowledge"
    )

    # 2. Hybrid Query Construction
    # We combine subject and body to capture both high-level intent and specific details
    search_query = f"SUBJECT: {subject} | CONTENT: {email_body[:1000]}"

    # 3. MMR Search (Maximal Marginal Relevance)
    # MMR selects docs that are relevant BUT diverse, avoiding 3 chunks of the same sentence.
    try:
        docs_with_scores = vector_store.similarity_search_with_relevance_scores(
            search_query, 
            k=1  # Initial pool to find diversity from
        )

        result = llm.invoke(f" format the answer according to the query {search_query} and the retrieved data is {docs_with_scores}")

        # 5. Handle "Knowledge Gap"
        if not result:
            print("⚠️ [RAG] No relevant context found in local database.")
            return {
                "retrieved_context": [], 
                "confidence_score": 0.0,
                "steps": state.get("steps", []) + ["RAG: No relevant docs found."]
            }

        print(f"✅ [RAG] Successfully retrieved {len(result.content)} chunks.")
        # print(f"✅ [RAG] Retrieved Context: {result.content}")

        return {
            "retrieved_context": result.content,
            "confidence_score": "1",
            "steps": state.get("steps", []) + [f"RAG: Found {len(result.content)} context chunks."]
        }

    except Exception as e:
        print(f"❌ [RAG ERROR]: {str(e)}")
        return {"retrieved_context": [], "confidence_score": 0.0}