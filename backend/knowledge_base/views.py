from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission
from .models import Document, ChatSession
from .serializers import DocumentSerializer, ChatSessionSerializer
from .utils.rag_helper import (
    extract_text_from_pdf,
    process_context_to_embeddings,
    query_rag_system,
    scrape_website_content,
    EmbeddingQuotaError,
    remove_source_from_vector_store,
    clear_all_vector_store_data,
)


class IsSuperUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)

class DocumentUploadView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]

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
        except ValueError as err:
            return Response({"error": str(err)}, status=503)
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
    permission_classes = [IsAuthenticated, IsSuperUser]

    def post(self, request):
        url = request.data.get('url')
        if not url:
            return Response({"error": "URL is required"}, status=400)
            
        # 1. Scrape the content
        raw_text = scrape_website_content(url)
        
        if raw_text:
            try:
                num_chunks = process_context_to_embeddings(raw_text, {"source": url})
            except ValueError as err:
                return Response({"error": str(err)}, status=503)
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


class AdminDocumentListView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]

    def get(self, request):
        documents = Document.objects.all().order_by('-uploaded_at')
        serializer = DocumentSerializer(documents, many=True)
        return Response(serializer.data)


class AdminDocumentDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]

    def delete(self, request, document_id):
        try:
            document = Document.objects.get(id=document_id)
        except Document.DoesNotExist:
            return Response({"error": "Document not found."}, status=404)

        source = document.url if document.source_type == 'url' else document.file.name

        try:
            remove_source_from_vector_store(source)
        except ValueError as err:
            return Response({"error": str(err)}, status=503)
        except Exception:
            return Response({"error": "Failed to clear processed context cache right now. Please try again."}, status=503)

        if document.file:
            document.file.delete(save=False)

        document.delete()
        return Response({"message": "Document removed successfully."}, status=200)


class AdminContextRefreshView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]

    def post(self, request):
        documents = Document.objects.all()
        removed_documents = documents.count()

        try:
            removed_vectors = clear_all_vector_store_data()
        except ValueError as err:
            return Response({"error": str(err)}, status=503)
        except Exception:
            return Response({"error": "Failed to clear context cache right now. Please try again."}, status=503)

        for document in documents:
            if document.file:
                document.file.delete(save=False)

        documents.delete()

        return Response(
            {
                "message": "Context cache refreshed successfully.",
                "removed_documents": removed_documents,
                "removed_vectors": removed_vectors,
            },
            status=200,
        )