# Updated views.py snippet
from requests import Response
from .services.rag_engine import RAGEngine
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatSession, Message


class ChatInterfaceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('query')
        session_id = request.data.get('session_id')

        # 1. Get or Create Session
        if session_id:
            session = ChatSession.objects.get(id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(user=request.user)

        # 2. Save User Message
        Message.objects.create(session=session, role='user', content=query)

        # 3. Get RAG Response
        engine = RAGEngine()
        result = engine.generate_response(query)

        # 4. Save AI Response
        Message.objects.create(session=session, role='ai', content=result['answer'])

        return Response({
            "session_id": session.id,
            "answer": result['answer'],
            "sources": result['sources']
        })

class ChatView(APIView):
    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({"error": "No query provided"}, status=400)

        engine = RAGEngine()
        result = engine.generate_response(query)
        
        return Response(result) # Returns {"answer": "...", "sources": [...]}
class ChatView(APIView):
    def post(self, request):
        user_query = request.data.get('query')
        
        # 1. Search for relevant context
        vector_db = get_vector_store()
        docs = vector_db.similarity_search(user_query, k=3) # Get top 3 paragraphs
        context = "\n\n".join([doc.page_content for doc in docs])

        # 2. Build the prompt
        prompt = f"""
        Answer the question based ONLY on the context below:
        Context: {context}
        Question: {user_query}
        """

        # 3. Call OpenAI (or your preferred LLM)
        # response = llm.invoke(prompt)
        
        return Response({"response": "AI Answer...", "sources": [d.metadata for d in docs]})