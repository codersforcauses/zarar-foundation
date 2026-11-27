from django.db import models
from django.utils import timezone


class PublishableContent(models.Model):
    """Abstract base model for publishable foundation content."""

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    summary = models.TextField(blank=True, default="")
    content = models.TextField()
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class News(PublishableContent):
    """News article published by foundation staff."""

    image = models.ImageField(upload_to="news/", blank=True)
    author = models.CharField(max_length=150, blank=True, default="")

    class Meta:
        verbose_name = "News Article"
        verbose_name_plural = "News"
        ordering = ["-published_at", "-created_at"]


class Event(PublishableContent):
    """Foundation event with schedule, location, and optional registration link."""

    image = models.ImageField(upload_to="events/", blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, default="")
    registration_url = models.URLField(blank=True, default="")

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-start_date", "-created_at"]


class Project(PublishableContent):
    """Foundation project with lifecycle status, location, and dates."""

    class Status(models.TextChoices):
        PLANNING = "PLANNING", "Planning"
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"

    image = models.ImageField(upload_to="projects/", blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    location = models.CharField(max_length=255, blank=True, default="")
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["-created_at"]
