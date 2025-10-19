from django.db import models
from django.contrib.auth.models import User


class Conversation(models.Model):
    """
    Chat conversation session for a user.
    Groups related queries together.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    title = models.CharField(
        max_length=255,
        help_text="Conversation title (auto-generated from first query)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'

    def __str__(self):
        return f"{self.user.email}: {self.title}"


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
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='queries',
        null=True,
        blank=True,
        help_text="Conversation this query belongs to"
    )
    question = models.TextField(help_text="User's legal question")
    image = models.ImageField(
        upload_to='query_images/',
        blank=True,
        null=True,
        help_text="Optional image attached to query"
    )
    answer = models.TextField(blank=True, help_text="AI-generated answer")
    sources = models.JSONField(
        default=list,
        help_text="Citations and source documents"
    )
    rating = models.IntegerField(
        null=True,
        blank=True,
        choices=[(1, 'Thumbs Down'), (5, 'Thumbs Up')],
        help_text="User feedback on response quality"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processing_time = models.FloatField(
        null=True,
        blank=True,
        help_text="Total time from query to completion (seconds)"
    )
    ttft = models.FloatField(
        null=True,
        blank=True,
        help_text="Time To First Token - PRD v2.1 NFR-1 (target: <5s P95)"
    )

    class Meta:
        db_table = 'queries'
        ordering = ['-created_at']
        verbose_name = 'Query'
        verbose_name_plural = 'Queries'

    def __str__(self):
        preview = self.question[:50] + "..." if len(self.question) > 50 else self.question
        return f"{self.user.email}: {preview}"
