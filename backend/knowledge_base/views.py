from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Document, ChatSession
from .serializers import DocumentSerializer, ChatSessionSerializer
from .utils.rag_helper import extract_text_from_pdf, query_rag_system

class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = DocumentSerializer(data=request.data)
        if serializer.is_valid():
            doc = serializer.save()
            # Trigger background processing (ideally via Celery)
            text = extract_text_from_pdf(doc.file.path)
            # embed_and_store(text, doc.id)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_query = request.data.get('query')
        session_id = request.data.get('session_id')
        
        # Get response from RAG util
        ai_response = query_rag_system(user_query)
        
        # Save to database for History feature
        # (Logic to save Message objects goes here)
        
        return Response({"response": ai_response})