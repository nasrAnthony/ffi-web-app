from pathlib import Path

from django.db import models
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify


def blog_image_upload_to(instance, filename):
    extension = Path(filename).suffix.lower() or ".jpg"
    base_slug = instance.slug or slugify(instance.title) or "blog-entry"
    return f"blog/{base_slug}{extension}"


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    summary = models.TextField(
        blank=True,
        help_text="Optional short summary shown on the main blog hub.",
    )
    main_image = models.ImageField(upload_to=blog_image_upload_to, blank=True, null=True)
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


@receiver(pre_save, sender=BlogPost)
def delete_replaced_blog_image(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = BlogPost.objects.get(pk=instance.pk)
    except BlogPost.DoesNotExist:
        return

    old_image = old_instance.main_image
    new_image = instance.main_image
    if old_image and old_image != new_image:
        old_image.delete(save=False)


@receiver(post_delete, sender=BlogPost)
def delete_blog_image_on_remove(sender, instance, **kwargs):
    if instance.main_image:
        instance.main_image.delete(save=False)
