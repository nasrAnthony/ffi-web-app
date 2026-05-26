from pathlib import Path

from django.db import models
from django.template.defaultfilters import slugify


def blog_image_upload_to(instance, filename):
    extension = Path(filename).suffix.lower() or ".jpg"
    base_slug = getattr(instance, "slug", "") or slugify(getattr(instance, "title", "")) or "blog-entry"
    return f"blog/{base_slug}{extension}"


class BlogPost(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    summary = models.TextField(
        blank=True,
        help_text="Optional short summary shown on the main blog hub.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PUBLISHED,
    )
    read_time_minutes = models.PositiveSmallIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def card_summary(self):
        if self.summary.strip():
            return self.summary.strip()

        first_section = self.sections.first()
        if not first_section:
            return ""

        text = first_section.body.strip()
        if len(text) <= 160:
            return text
        return f"{text[:157].rstrip()}..."

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        base_slug = slugify(self.title) or "blog-entry"
        candidate = base_slug
        suffix = 2

        while BlogPost.objects.exclude(pk=self.pk).filter(slug=candidate).exists():
            candidate = f"{base_slug}-{suffix}"
            suffix += 1

        return candidate


class BlogSection(models.Model):
    post = models.ForeignKey(BlogPost, related_name="sections", on_delete=models.CASCADE)
    heading = models.CharField(max_length=255)
    body = models.TextField(help_text="Use blank lines to separate paragraphs.")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.post.title} - {self.heading}"
