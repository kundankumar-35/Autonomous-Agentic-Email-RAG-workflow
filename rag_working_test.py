from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()

# 1. Setup
local_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = Chroma(
    persist_directory="./knowledge_base",
    embedding_function=local_embeddings,
    collection_name="corporate_knowledge"
)

# 2. Test Search
query = "Who is bhavya garg and find the email id of him and cgpa and currently which year they studying in 10000 characters maximum?"
results = vector_store.similarity_search_with_relevance_scores(query, k=1)

llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
result = llm.invoke(f" format the answer according to the query {query} and the result is {results}")


print(f"🔎 Search results for: '{query}'")
print(result.content)
# for doc, score in results:
#     print(f"✅ Found match (Score: {score:.4f}):")
#     print(f"--- CONTENT: {doc.page_content[:2000]}...")