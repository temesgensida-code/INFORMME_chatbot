import requests
from bs4 import BeautifulSoup
import PyPDF2
import re
import time

# --- EXTRACTION TOOLS ---

def extract_text_from_pdf(file_path):
    """Extracts text from uploaded PDF files."""
    text = ""
    try:
        with open(file_path, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return text

def scrape_website_content(url):
    """
    Scrapes a website, removes scripts/styles, 
    and extracts paragraph text.
    """
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove noise (scripts, styles, nav, footers)
        for script_or_style in soup(["script", "style", "nav", "footer", "header"]):
            script_or_style.decompose()

        # Focus on paragraphs
        paragraphs = soup.find_all('p')
        text = "\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
        
        return text
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

# --- RAG PROCESSING ---

def split_text_chunks(raw_text, chunk_size=1000, chunk_overlap=100):
    """Simple local text splitter to avoid hard dependency on langchain splitters."""
    if not raw_text:
        return []

    chunks = []
    start = 0
    text_length = len(raw_text)

    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunks.append(raw_text[start:end])
        if end == text_length:
            break
        start = max(0, end - chunk_overlap)

    return chunks

def process_context_to_embeddings(raw_text, source_metadata):
    """
    Chunks text and prepares it for the Vector Database.
    This works for both Scraped content and PDF content.
    """
    # 1. Split text into manageable pieces (chunks)
    chunks = split_text_chunks(
        raw_text,
        chunk_size=RAG_CHUNK_SIZE,
        chunk_overlap=RAG_CHUNK_OVERLAP,
    )
    if RAG_MAX_CHUNKS_PER_DOC > 0:
        chunks = chunks[:RAG_MAX_CHUNKS_PER_DOC]
    
    # 2. Embedding & Storage Logic
    # Example: 
    # vector_db.add_texts(chunks, metadatas=[source_metadata] * len(chunks))
    embed_and_store(raw_text, source_metadata, chunks=chunks)
    return len(chunks)

def query_rag_system(user_query):
    """
    1. Embed user_query
    2. Retrieve top-k chunks from Vector DB
    3. Generate LLM response using retrieved chunks
    """
    # retrieved_context = vector_db.similarity_search(user_query)
    # response = llm.generate(prompt=user_query, context=retrieved_context)
    return "AI response based on context..."

import os
import sys
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Directory where your vector data will live
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../../vector_db")
COLLECTION_NAME = "project_knowledge_base"
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "2500"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "200"))
RAG_MAX_CHUNKS_PER_DOC = int(os.getenv("RAG_MAX_CHUNKS_PER_DOC", "40"))


class EmbeddingQuotaError(Exception):
    pass


def _extract_retry_seconds(error_text):
    match = re.search(r"retry in\s*([0-9]+(?:\.[0-9]+)?)s", error_text, flags=re.IGNORECASE)
    if match:
        return float(match.group(1))

    match = re.search(r"retryDelay'?:\s*'([0-9]+)s", error_text, flags=re.IGNORECASE)
    if match:
        return float(match.group(1))

    return 5.0

def get_vector_store():
    """Initializes or loads the Chroma database."""
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
        if sys.version_info >= (3, 14):
            raise ValueError(
                "Chroma/Chromadb is currently incompatible with Python 3.14+. "
                "Use Python 3.12 or 3.11 for vector DB (recreate your venv, then reinstall requirements)."
            ) from err
        raise

    embedding_model = os.getenv("GEMINI_EMBEDDING_MODEL", "models/gemini-embedding-001")
    embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model, google_api_key=google_api_key)
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )

def embed_and_store(raw_text, metadata, chunks=None):
    """Chunks text and saves it to the vector database."""
    # 1. Split text so the AI can find specific answers
    if chunks is None:
        chunks = split_text_chunks(
            raw_text,
            chunk_size=RAG_CHUNK_SIZE,
            chunk_overlap=RAG_CHUNK_OVERLAP,
        )
        if RAG_MAX_CHUNKS_PER_DOC > 0:
            chunks = chunks[:RAG_MAX_CHUNKS_PER_DOC]

    if not chunks:
        return 0
    
    # 2. Add chunks to Chroma
    vector_db = get_vector_store()

    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        try:
            vector_db.add_texts(texts=chunks, metadatas=[metadata] * len(chunks))
            break
        except Exception as err:
            error_text = str(err)
            lower_text = error_text.lower()

            is_quota_error = "resource_exhausted" in lower_text or "429" in lower_text or "quota" in lower_text
            if not is_quota_error:
                raise

            if attempt == max_attempts:
                retry_seconds = _extract_retry_seconds(error_text)
                raise EmbeddingQuotaError(
                    f"Embedding quota exceeded. Please wait about {int(retry_seconds) + 1} seconds and try again."
                ) from err

            sleep_seconds = min(_extract_retry_seconds(error_text), 10)
            time.sleep(sleep_seconds)
    
    return len(chunks)


def remove_source_from_vector_store(source):
    """Removes all vector entries associated with a given source metadata value."""
    if not source:
        return

    vector_db = get_vector_store()
    vector_db.delete(where={"source": source})