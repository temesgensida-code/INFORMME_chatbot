import os

from langchain_google_genai import ChatGoogleGenerativeAI
try:
    from langchain.prompts import ChatPromptTemplate
except ModuleNotFoundError:
    # LangChain split prompts into langchain_core in newer releases.
    from langchain_core.prompts import ChatPromptTemplate
from .vectore_store import get_vector_db

class RAGEngine:
    def __init__(self):
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GOOGLE_API_KEY is not configured.")

        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        self.llm = ChatGoogleGenerativeAI(model=model_name, temperature=0, google_api_key=google_api_key)
        self.db = get_vector_db()

    def generate_response(self, user_query):
        """
        Full RAG pipeline: 
        1. Retrieve relevant documents
        2. Format prompt
        3. Get LLm response
        """
        # 1. Similarity Search (Retrieve top 4 relevant chunks)
        results = self.db.similarity_search(user_query, k=4)
        
        # Combine context
        context_text = "\n\n---\n\n".join([doc.page_content for doc in results])
        sources = list(set([doc.metadata.get('source') for doc in results]))

        # 2. Define the Prompt Template
        template = """
        You are a helpful assistant for our website. Use the following pieces of context 
        to answer the user's question. If you don't know the answer based on the context, 
        just say you don't know, don't try to make up an answer.

        Context:
        {context}

        Question: 
        {question}

        Answer (be concise and professional):
        """
        
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | self.llm

        # 3. Invoke LLM
        try:
            response = chain.invoke({
                "context": context_text,
                "question": user_query
            })
            answer_text = response.content
        except Exception as err:
            error_text = str(err).lower()
            if "insufficient_quota" in error_text or "error code: 429" in error_text or "quota" in error_text:
                fallback = context_text.strip()
                if not fallback:
                    fallback = "No indexed context is available yet. Please upload a PDF or process a URL first."

                answer_text = (
                    "Gemini quota is currently exceeded, so this is a context-only fallback response:\n\n"
                    f"{fallback[:1200]}"
                )
            else:
                raise

        return {
            "answer": answer_text,
            "sources": sources
        }