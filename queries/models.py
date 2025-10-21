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


class SystemPrompt(models.Model):
    """
    System prompt for RAG responses.
    Editable by admin users.
    Only one active prompt at a time.
    """
    prompt_text = models.TextField(
        help_text="System prompt used for RAG responses",
        default="""Jesteś Somsiad - pomocnym asystentem prawnym dla polskich właścicieli domów jednorodzinnych.

Twoim zadaniem jest udzielanie jasnych, rzeczowych odpowiedzi na pytania prawne dotyczące:
- Budownictwa i remontów
- Ogrodów i działek
- Przeglądów technicznych
- Sporów sąsiedzkich

Zasady odpowiedzi:
1. Odpowiadaj TYLKO na podstawie dostarczonych źródeł prawnych
2. Cytuj konkretne artykuły i przepisy
3. Używaj prostego języka, unikaj zbędnego żargonu prawnego
4. Jeśli nie masz pewności lub źródła nie zawierają odpowiedzi, powiedz to wprost
5. W razie potrzeby zasugeruj konsultację z prawnikiem

Format odpowiedzi:
- Krótkie podsumowanie (1-2 zdania)
- Szczegółowa odpowiedź z odnies
ieniami do przepisów
- Praktyczne wskazówki (jeśli masz pewność)"""
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Admin who last updated this prompt"
    )

    class Meta:
        db_table = 'system_prompts'
        ordering = ['-updated_at']
        verbose_name = 'System Prompt'
        verbose_name_plural = 'System Prompts'

    def __str__(self):
        status = "Active" if self.is_active else "Inactive"
        return f"System Prompt ({status}) - Updated {self.updated_at.strftime('%Y-%m-%d %H:%M')}"

    def save(self, *args, **kwargs):
        # Ensure only one active prompt
        if self.is_active:
            SystemPrompt.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
