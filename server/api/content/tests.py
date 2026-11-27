import tempfile
from io import BytesIO

from PIL import Image
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .admin import EventAdmin, NewsAdmin, ProjectAdmin
from .models import Event, News, Project

User = get_user_model()


def create_test_image(name="test.png"):
    buffer = BytesIO()
    Image.new("RGB", (10, 10), color="red").save(buffer, format="PNG")
    buffer.seek(0)
    return SimpleUploadedFile(name, buffer.read(), content_type="image/png")


class ContentModelTests(TestCase):
    def test_news_str_and_auto_published_at(self):
        draft = News.objects.create(
            title="Draft News",
            slug="draft-news",
            content="Body text",
        )
        self.assertEqual(str(draft), "Draft News")
        self.assertFalse(draft.is_published)
        self.assertIsNone(draft.published_at)

        draft.is_published = True
        draft.save()
        self.assertIsNotNone(draft.published_at)

    def test_event_str(self):
        event = Event.objects.create(
            title="Annual Gala",
            slug="annual-gala",
            content="Join us",
            start_date=timezone.now(),
            location="Perth",
        )
        self.assertEqual(str(event), "Annual Gala")

    def test_project_str_and_default_status(self):
        project = Project.objects.create(
            title="Clean Water Initiative",
            slug="clean-water-initiative",
            content="Project details",
        )
        self.assertEqual(str(project), "Clean Water Initiative")
        self.assertEqual(project.status, Project.Status.ACTIVE)


class ContentAdminTests(TestCase):
    def setUp(self):
        self.staff_user = User.objects.create_superuser(
            username="staff",
            email="staff@example.com",
            password="Password123!",
        )
        self.client.force_login(self.staff_user)

    def test_models_registered_in_admin(self):
        self.assertIsInstance(site._registry.get(News), NewsAdmin)
        self.assertIsInstance(site._registry.get(Event), EventAdmin)
        self.assertIsInstance(site._registry.get(Project), ProjectAdmin)

    def test_admin_changelist_and_search(self):
        News.objects.create(title="Alpha Update", slug="alpha-update", content="Details", is_published=True)
        News.objects.create(title="Beta Story", slug="beta-story", content="Other", is_published=False)
        Event.objects.create(
            title="Community Meetup",
            slug="community-meetup",
            content="Event info",
            start_date=timezone.now(),
            location="Sydney",
            is_published=True,
        )
        Project.objects.create(title="Solar Microgrid", slug="solar-microgrid", content="Solar details", location="Rural")

        for model, query, expected, unexpected in [
            (News, "Alpha", "Alpha Update", "Beta Story"),
            (Event, "Sydney", "Community Meetup", None),
            (Project, "Solar", "Solar Microgrid", None),
        ]:
            url = reverse(f"admin:content_{model._meta.model_name}_changelist")
            response = self.client.get(url, {"q": query})
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, expected)
            if unexpected:
                self.assertNotContains(response, unexpected)

    def test_admin_unpublish_action(self):
        news = News.objects.create(title="Published News", slug="published-news", content="Body", is_published=True)
        event = Event.objects.create(
            title="Published Event",
            slug="published-event",
            content="Body",
            start_date=timezone.now(),
            is_published=True,
        )
        project = Project.objects.create(title="Published Project", slug="published-project", content="Body", is_published=True)

        for model, obj in [(News, news), (Event, event), (Project, project)]:
            url = reverse(f"admin:content_{model._meta.model_name}_changelist")
            response = self.client.post(
                url,
                {
                    "action": "unpublish_selected",
                    "_selected_action": [str(obj.pk)],
                },
                follow=True,
            )
            self.assertEqual(response.status_code, 200)
            obj.refresh_from_db()
            self.assertFalse(obj.is_published)

    def test_image_upload_saves_to_media_and_renders_preview(self):
        with tempfile.TemporaryDirectory() as tmp_media:
            with override_settings(MEDIA_ROOT=tmp_media):
                for model, subdir in [(News, "news/"), (Event, "events/"), (Project, "projects/")]:
                    kwargs = {
                        "title": f"{model.__name__} With Image",
                        "slug": f"{model._meta.model_name}-with-image",
                        "content": "Content with image",
                        "image": create_test_image(f"{model._meta.model_name}.png"),
                    }
                    if model is Event:
                        kwargs["start_date"] = timezone.now()

                    obj = model.objects.create(**kwargs)
                    self.assertTrue(obj.image.name.startswith(subdir))

                    change_url = reverse(f"admin:content_{model._meta.model_name}_change", args=[obj.pk])
                    response = self.client.get(change_url)
                    self.assertEqual(response.status_code, 200)
                    self.assertContains(response, f'<img src="{obj.image.url}"')
                    obj.image.close()
