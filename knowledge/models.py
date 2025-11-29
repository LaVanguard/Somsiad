from django.db import models


class Document(models.Model):
    """
    Legal document (PDF) uploaded by admin for RAG knowledge base.
    Sprint 2 implementation.
    """

    title = models.CharField(max_length=255, help_text="Document title")
    file = models.FileField(upload_to="documents/", help_text="PDF file")
    category = models.CharField(
        max_length=100,
        help_text="Document category (e.g., 'budowa', 'ogród', 'elektryka')",
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(
        default=False, help_text="Has this document been processed for embeddings?"
    )

    class Meta:
        db_table = "documents"
        ordering = ["-uploaded_at"]
        verbose_name = "Document"
        verbose_name_plural = "Documents"

    def __str__(self):
        return f"{self.title} ({self.category})"


class Embedding(models.Model):
    """
    Vector embedding for RAG retrieval.
    Links document chunks to Supabase pgvector storage.
    Sprint 2 implementation.
    """

    document = models.ForeignKey(
        Document, on_delete=models.CASCADE, related_name="embeddings"
    )
    chunk_text = models.TextField(help_text="Original text chunk from document")
    embedding_id = models.CharField(
        max_length=100, help_text="Supabase vector ID for this embedding"
    )
    metadata = models.JSONField(
        default=dict, help_text="Metadata: page number, section, etc."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "embeddings"
        ordering = ["document", "id"]
        verbose_name = "Embedding"
        verbose_name_plural = "Embeddings"

    def __str__(self):
        return f"Embedding for {self.document.title} (ID: {self.embedding_id})"
