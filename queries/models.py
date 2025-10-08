from django.db import models
from django.contrib.auth.models import User


class Query(models.Model):
    """
    User query with RAG-generated response.
    Stores conversation history.
    Sprint 2 implementation.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='queries'
    )
    question = models.TextField(help_text="User's legal question")
    answer = models.TextField(blank=True, help_text="AI-generated answer")
    sources = models.JSONField(
        default=list,
        help_text="Citations and source documents"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processing_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Time taken to generate response (seconds)"
    )

    class Meta:
        db_table = 'queries'
        ordering = ['-created_at']
        verbose_name = 'Query'
        verbose_name_plural = 'Queries'

    def __str__(self):
        preview = self.question[:50] + "..." if len(self.question) > 50 else self.question
        return f"{self.user.email}: {preview}"
