import json
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .blog_batch_import import SESSION_KEY, parse_blog_batch_json
from .models import BlogPost


TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix="ffi-test-media-")


def build_batch_json(payload):
    return SimpleUploadedFile(
        "blog_batch.json",
        json.dumps(payload).encode("utf-8"),
        content_type="application/json",
    )


@override_settings(
    MEDIA_ROOT=TEST_MEDIA_ROOT,
    DEFAULT_FROM_EMAIL="test@example.com",
    INTERNAL_CONTACT="internal@example.com",
)
class BlogBatchImportTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="password123",
            email="admin@example.com",
        )
        self.client.force_login(self.admin_user)

    def test_parse_blog_batch_json_generates_preview_data(self):
        uploaded_file = build_batch_json(
            {
                "schema_version": "1.0",
                "business_name": "Family First Insurances",
                "business_location": "Ottawa, Ontario, Canada",
                "batch_status": "draft",
                "posts": [
                    {
                        "title": "Tenant Insurance in Ottawa",
                        "slug": "",
                        "summary": "A practical guide for renters.",
                        "status": "draft",
                        "read_time_minutes": 7,
                        "blog_sections": [
                            {
                                "order": 1,
                                "heading": "Why it matters",
                                "body": "Tenant insurance protects your belongings.",
                            }
                        ],
                    }
                ],
            }
        )

        batch = parse_blog_batch_json(uploaded_file)

        self.assertEqual(batch.batch_status, BlogPost.Status.DRAFT)
        self.assertEqual(batch.schema_version, "1.0")
        self.assertEqual(len(batch.posts), 1)
        self.assertEqual(batch.posts[0]["slug"], "tenant-insurance-in-ottawa")
        self.assertEqual(batch.posts[0]["read_time_minutes"], 7)

    def test_admin_bulk_import_creates_posts_only_after_confirmation(self):
        upload_url = reverse("admin:app_blogpost_bulk_import")
        preview_url = reverse("admin:app_blogpost_bulk_import_preview")
        confirm_url = reverse("admin:app_blogpost_bulk_import_confirm")

        uploaded_file = build_batch_json(
            {
                "schema_version": "1.0",
                "batch_status": "draft",
                "posts": [
                    {
                        "title": "Home Insurance Tips for New Buyers",
                        "summary": "Helpful pointers before you purchase.",
                        "status": "draft",
                        "read_time_minutes": 6,
                        "blog_sections": [
                            {
                                "order": 1,
                                "heading": "Start with the basics",
                                "body": "Review your coverage limits and deductibles.",
                            }
                        ],
                    }
                ],
            }
        )

        response = self.client.post(upload_url, {"batch_file": uploaded_file})
        self.assertRedirects(response, preview_url)
        self.assertEqual(BlogPost.objects.count(), 0)
        self.assertIn(SESSION_KEY, self.client.session)

        preview_response = self.client.get(preview_url)
        self.assertContains(preview_response, "Home Insurance Tips for New Buyers")
        self.assertContains(preview_response, "Will publish")

        confirm_response = self.client.post(confirm_url)
        changelist_url = reverse("admin:app_blogpost_changelist")
        self.assertRedirects(confirm_response, changelist_url)

        post = BlogPost.objects.get()
        self.assertEqual(post.status, BlogPost.Status.PUBLISHED)
        self.assertEqual(post.read_time_minutes, 6)
        self.assertEqual(post.sections.count(), 1)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_public_blog_hides_draft_posts(self):
        draft_post = BlogPost.objects.create(
            title="Draft post",
            slug="draft-post",
            status=BlogPost.Status.DRAFT,
            read_time_minutes=4,
        )
        published_post = BlogPost.objects.create(
            title="Published post",
            slug="published-post",
            status=BlogPost.Status.PUBLISHED,
            read_time_minutes=5,
        )

        response = self.client.get(reverse("blog"))
        self.assertContains(response, published_post.title)
        self.assertNotContains(response, draft_post.title)

        article_response = self.client.get(reverse("blog-article", args=[draft_post.slug]))
        self.assertEqual(article_response.status_code, 404)
