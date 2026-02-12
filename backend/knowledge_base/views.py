from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Document, ChatSession
from .serializers import DocumentSerializer, ChatSessionSerializer
from .utils.rag_helper import (
    extract_text_from_pdf,
    process_context_to_embeddings,
    query_rag_system,
    scrape_website_content,
    EmbeddingQuotaError,
)

class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            return Response({"error": "PDF file is required."}, status=400)

        title = request.data.get('title') or uploaded_file.name
        doc = Document.objects.create(
            title=title,
            source_type='pdf',
            file=uploaded_file,
            is_processed=False,
        )

        text = extract_text_from_pdf(doc.file.path)
        if not text.strip():
            return Response({"error": "Could not extract text from PDF."}, status=400)

        try:
            chunks = process_context_to_embeddings(text, {"source": doc.file.name})
        except EmbeddingQuotaError as err:
            return Response({"error": str(err)}, status=429)
        except Exception:
            return Response({"error": "Failed to process PDF content right now. Please try again."}, status=503)

        doc.is_processed = True
        doc.save(update_fields=['is_processed'])

        return Response(
            {
                "message": f"PDF processed successfully with {chunks} chunks.",
                "document": {
                    "id": doc.id,
                    "title": doc.title,
                    "source_type": doc.source_type,
                    "is_processed": doc.is_processed,
                },
            },
            status=201,
        )
    
# In views.py
class WebsiteLinkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        url = request.data.get('url')
        if not url:
            return Response({"error": "URL is required"}, status=400)
            
        # 1. Scrape the content
        raw_text = scrape_website_content(url)
        
        if raw_text:
            try:
                num_chunks = process_context_to_embeddings(raw_text, {"source": url})
            except EmbeddingQuotaError as err:
                return Response({"error": str(err)}, status=429)
            except Exception:
                return Response({"error": "Failed to process website content right now. Please try again."}, status=503)

            doc = Document.objects.create(
                title=f"Scraped: {url}",
                source_type='url',
                url=url,
                is_processed=True,
            )

            return Response(
                {
                    "message": f"Successfully processed {num_chunks} chunks from {url}",
                    "document": {
                        "id": doc.id,
                        "title": doc.title,
                        "source_type": doc.source_type,
                        "is_processed": doc.is_processed,
                    },
                },
                status=201,
            )
        
        return Response({"error": "Failed to extract content from URL"}, status=500)

class ChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user_query = request.data.get('query')
        if not user_query:
            return Response({"error": "Query is required."}, status=400)
        
        ai_response = query_rag_system(user_query)

        return Response({"response": ai_response})