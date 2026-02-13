from .services.rag_engine import RAGEngine
from django.conf import settings
from django.http import StreamingHttpResponse
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ChatSession, Message


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        latest_session = (
            ChatSession.objects
            .filter(user=request.user)
            .order_by('-updated_at')
            .first()
        )

        if not latest_session:
            return Response({
                "session_id": None,
                "messages": [],
            })

        messages = [
            {
                "role": message.role,
                "content": message.content,
                "timestamp": message.timestamp,
            }
            for message in latest_session.messages.all()
        ]

        return Response({
            "session_id": latest_session.id,
            "messages": messages,
        })


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


class ChatInterfaceStreamView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('query')
        if not query:
            return Response({"error": "Query is required."}, status=400)

        session_id = request.data.get('session_id')

        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                return Response({"error": "Invalid session_id."}, status=404)
        else:
            session = ChatSession.objects.create(user=request.user)

        Message.objects.create(session=session, role='user', content=query)

        try:
            engine = RAGEngine()
            stream_iterator, sources = engine.stream_response(query)
        except ValueError as err:
            return Response({"error": str(err)}, status=503)
        except Exception as err:
            if settings.DEBUG:
                return Response({"error": str(err)}, status=503)
            return Response({"error": "AI service is currently unavailable."}, status=503)

        def stream():
            answer_parts = []

            try:
                for piece in stream_iterator:
                    answer_parts.append(piece)
                    yield json.dumps({"type": "chunk", "content": piece}) + "\n"

                final_answer = "".join(answer_parts).strip()
                if final_answer:
                    Message.objects.create(session=session, role='ai', content=final_answer)

                yield json.dumps({
                    "type": "done",
                    "session_id": session.id,
                    "sources": sources,
                }) + "\n"
            except Exception as err:
                error_message = str(err) if settings.DEBUG else "AI service is currently unavailable."
                yield json.dumps({"type": "error", "error": error_message}) + "\n"

        response = StreamingHttpResponse(stream(), content_type='application/x-ndjson')
        response['Cache-Control'] = 'no-cache'
        return response