import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def load_and_index_data():
    # 1. Setup paths
    DATA_PATH = "rag_data/"
    DB_PATH = "./knowledge_base"
    
    print("📂 Loading documents...")
    # Supports both .txt and .pdf
    # loader = DirectoryLoader(DATA_PATH, glob="**/*.txt", loader_cls=TextLoader)
    # If you have PDFs, uncomment the next line:
    loader = DirectoryLoader(DATA_PATH, glob="**/*.pdf", loader_cls=PyPDFLoader)
    
    docs = loader.load()

    # 2. Split text into chunks (Crucial for RAG)
    # We use 1000 character chunks with a 200 character overlap
    # This ensures "context" isn't cut off in the middle of a sentence
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        add_start_index=True
    )
    splits = text_splitter.split_documents(docs)
    print(f"✂️ Split into {len(splits)} chunks.")

    local_embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    # 3. Create Embeddings and Store in ChromaDB
    print("🧠 Creating embeddings and saving to DB...")
    vector_store = Chroma.from_documents(
        documents=splits,
        embedding=local_embeddings,
        persist_directory=DB_PATH,
        collection_name="corporate_knowledge"
    )
    
    print(f"✅ Success! Database saved at {DB_PATH}")

if __name__ == "__main__":
    load_and_index_data()