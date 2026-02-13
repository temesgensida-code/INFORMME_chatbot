import os
import sys
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

    try:
        from langchain_chroma import Chroma
    except ModuleNotFoundError as err:  # pragma: no cover
        raise ValueError(
            "Vector DB dependencies are not installed. Install 'langchain-chroma' and 'chromadb' to enable RAG."
        ) from err
    except Exception as err:  # pragma: no cover
        # Chroma/Chromadb currently relies on Pydantic v1 compatibility layers that
        # are not compatible with Python 3.14+.
        if sys.version_info >= (3, 14):
            raise ValueError(
                "Chroma/Chromadb is currently incompatible with Python 3.14+. "
                "Use Python 3.12 or 3.11 for the chatbot RAG features (recreate your venv, then reinstall requirements)."
            ) from err
        raise

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