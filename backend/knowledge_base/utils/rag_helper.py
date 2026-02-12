import requests
from bs4 import BeautifulSoup
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter

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

def process_context_to_embeddings(raw_text, source_metadata):
    """
    Chunks text and prepares it for the Vector Database.
    This works for both Scraped content and PDF content.
    """
    # 1. Split text into manageable pieces (chunks)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100
    )
    chunks = text_splitter.split_text(raw_text)
    
    # 2. Embedding & Storage Logic
    # Example: 
    # vector_db.add_texts(chunks, metadatas=[source_metadata] * len(chunks))
    
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
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitter import RecursiveCharacterTextSplitter

# Directory where your vector data will live
CHROMA_PATH = os.path.join(os.path.dirname(__file__), "../../vector_db")

def get_vector_store():
    """Initializes or loads the Chroma database."""
    embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
        collection_name="website_knowledge"
    )

def embed_and_store(raw_text, metadata):
    """Chunks text and saves it to the vector database."""
    # 1. Split text so the AI can find specific answers
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(raw_text)
    
    # 2. Add chunks to Chroma
    vector_db = get_vector_store()
    vector_db.add_texts(texts=chunks, metadatas=[metadata] * len(chunks))
    
    return len(chunks)