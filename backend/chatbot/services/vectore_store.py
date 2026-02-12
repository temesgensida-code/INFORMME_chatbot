import os
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# Define where the vector data is stored
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../../../vector_db")

def get_vector_db():
    """
    Returns an instance of the Chroma vector store.
    Ensure OPENAI_API_KEY is set in your environment variables.
    """
    embeddings = OpenAIEmbeddings()
    
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name="project_knowledge_base"
    )

def add_to_vector_store(text_chunks, metadata):
    """
    Adds new chunks to the database.
    metadata: dict containing 'source' (URL or Filename)
    """
    db = get_vector_db()
    db.add_texts(texts=text_chunks, metadatas=[metadata] * len(text_chunks))