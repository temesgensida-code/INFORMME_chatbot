import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Define where the vector data is stored
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../../vector_db")
COLLECTION_NAME = "project_knowledge_base"

def get_vector_db():
    """
    Returns an instance of the Chroma vector store.
    Ensure GOOGLE_API_KEY is set in your environment variables.
    """
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        raise ValueError("GOOGLE_API_KEY is not configured.")

    embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
    embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model, google_api_key=google_api_key)
    
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

def add_to_vector_store(text_chunks, metadata):
    """
    Adds new chunks to the database.
    metadata: dict containing 'source' (URL or Filename)
    """
    db = get_vector_db()
    db.add_texts(texts=text_chunks, metadatas=[metadata] * len(text_chunks))