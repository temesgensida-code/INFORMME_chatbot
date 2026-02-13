from .services.rag_engine import RAGEngine
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatSession, Message


class ChatInterfaceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({"error": "Query is required."}, status=400)

        session_id = request.data.get('session_id')

        # 1. Get or Create Session
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({"error": "Invalid session_id."}, status=404)
        else:
            session = ChatSession.objects.create(user=request.user)

        # 2. Save User Message
        Message.objects.create(session=session, role='user', content=query)

        # 3. Get RAG Response
        try:
            engine = RAGEngine()
            result = engine.generate_response(query)
        except ValueError as err:
            return Response({"error": str(err)}, status=503)
        except Exception as err:
            if settings.DEBUG:
                return Response({"error": str(err)}, status=503)
            return Response({"error": "AI service is currently unavailable."}, status=503)

        # 4. Save AI Response
        Message.objects.create(session=session, role='ai', content=result['answer'])

        return Response({
            "session_id": session.id,
            "answer": result['answer'],
            "sources": result['sources']
        })