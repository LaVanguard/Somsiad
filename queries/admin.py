from django.contrib import admin

from .models import Conversation, Query


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "query_count", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("user__email", "title")
    readonly_fields = ("created_at", "updated_at")

    def query_count(self, obj):
        return obj.queries.count()

    query_count.short_description = "Messages"


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "conversation",
        "question_preview",
        "rating",
        "created_at",
        "processing_time",
    )
    list_filter = ("rating", "created_at")
    search_fields = ("user__email", "question", "answer")
    readonly_fields = ("created_at", "processing_time")

    fieldsets = (
        (
            "User & Conversation",
            {"fields": ("user", "conversation", "question", "image")},
        ),
        ("Response", {"fields": ("answer", "sources", "rating")}),
        ("Metadata", {"fields": ("created_at", "processing_time")}),
    )

    def question_preview(self, obj):
        return obj.question[:75] + "..." if len(obj.question) > 75 else obj.question

    question_preview.short_description = "Question"
