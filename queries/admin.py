from django.contrib import admin
from .models import Query


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ('user', 'question_preview', 'rating', 'created_at', 'processing_time')
    list_filter = ('rating', 'created_at')
    search_fields = ('user__email', 'question', 'answer')
    readonly_fields = ('created_at', 'processing_time')

    fieldsets = (
        ('User & Question', {
            'fields': ('user', 'question', 'image')
        }),
        ('Response', {
            'fields': ('answer', 'sources', 'rating')
        }),
        ('Metadata', {
            'fields': ('created_at', 'processing_time')
        }),
    )

    def question_preview(self, obj):
        return obj.question[:75] + "..." if len(obj.question) > 75 else obj.question
    question_preview.short_description = 'Question'
