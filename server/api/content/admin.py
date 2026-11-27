from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Event, News, Project


class BaseContentAdmin(admin.ModelAdmin):
    """Shared admin configuration for publishable content models."""

    list_editable = ("is_published",)
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("image_preview", "created_at", "updated_at")
    actions = ("publish_selected", "unpublish_selected")

    @admin.display(description="Image Preview")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" alt="{}" style="max-height: 200px; max-width: 300px; object-fit: contain;" />',
                obj.image.url,
                obj.title,
            )
        return "No image uploaded"

    @admin.display(description="Thumbnail")
    def image_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" alt="{}" style="max-height: 40px; max-width: 60px; object-fit: cover;" />',
                obj.image.url,
                obj.title,
            )
        return "—"

    @admin.action(description="Publish selected items")
    def publish_selected(self, request, queryset):
        now = timezone.now()
        queryset.filter(published_at__isnull=True).update(
            is_published=True,
            published_at=now,
        )
        queryset.update(is_published=True)

    @admin.action(description="Unpublish selected items")
    def unpublish_selected(self, request, queryset):
        queryset.update(is_published=False)


@admin.register(News)
class NewsAdmin(BaseContentAdmin):
    list_display = ("title", "author", "is_published", "published_at", "image_thumbnail", "updated_at")
    list_filter = ("is_published", "published_at", "created_at")
    search_fields = ("title", "summary", "content", "author")
    fieldsets = (
        (None, {"fields": ("title", "slug", "author", "summary", "content")}),
        ("Media", {"fields": ("image", "image_preview")}),
        ("Publishing", {"fields": ("is_published", "published_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Event)
class EventAdmin(BaseContentAdmin):
    list_display = ("title", "start_date", "location", "is_published", "image_thumbnail", "updated_at")
    list_filter = ("is_published", "start_date", "created_at")
    search_fields = ("title", "summary", "content", "location")
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "content")}),
        ("Event Details", {"fields": ("start_date", "end_date", "location", "registration_url")}),
        ("Media", {"fields": ("image", "image_preview")}),
        ("Publishing", {"fields": ("is_published", "published_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Project)
class ProjectAdmin(BaseContentAdmin):
    list_display = ("title", "status", "location", "is_published", "image_thumbnail", "updated_at")
    list_filter = ("is_published", "status", "created_at")
    search_fields = ("title", "summary", "content", "location")
    fieldsets = (
        (None, {"fields": ("title", "slug", "status", "summary", "content")}),
        ("Project Details", {"fields": ("location", "start_date", "end_date")}),
        ("Media", {"fields": ("image", "image_preview")}),
        ("Publishing", {"fields": ("is_published", "published_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
