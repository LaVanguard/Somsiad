from django.contrib import admin
from .models import Document, Embedding


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'processed', 'uploaded_at')
    list_filter = ('category', 'processed', 'uploaded_at')
    search_fields = ('title', 'category')
    readonly_fields = ('uploaded_at',)

    fieldsets = (
        ('Document Information', {
            'fields': ('title', 'category', 'file')
        }),
        ('Processing Status', {
            'fields': ('processed', 'uploaded_at')
        }),
    )


@admin.register(Embedding)
class EmbeddingAdmin(admin.ModelAdmin):
    list_display = ('document', 'embedding_id', 'created_at')
    list_filter = ('document', 'created_at')
    search_fields = ('document__title', 'chunk_text', 'embedding_id')
    readonly_fields = ('created_at',)

    fieldsets = (
        ('Embedding Information', {
            'fields': ('document', 'chunk_text', 'embedding_id')
        }),
        ('Metadata', {
            'fields': ('metadata', 'created_at')
        }),
    )
