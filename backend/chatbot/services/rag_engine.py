from langchain_openai import ChatOpenAI
try:
    from langchain.prompts import ChatPromptTemplate
except ModuleNotFoundError:
    # LangChain split prompts into langchain_core in newer releases.
    from langchain_core.prompts import ChatPromptTemplate
from .vectore_store import get_vector_db

class RAGEngine:
    def __init__(self):
        # Initialize the LLM (GPT-4o or 3.5-turbo)
        self.llm = ChatOpenAI(model_name="gpt-4o", temperature=0)
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
        response = chain.invoke({
            "context": context_text,
            "question": user_query
        })

        return {
            "answer": response.content,
            "sources": sources
        }