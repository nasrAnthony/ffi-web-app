from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt
from types import SimpleNamespace
from .models import BlogPost, BlogSection
from .forms import BlogBatchUploadForm, BlogPostAdminForm
from .blog_batch_import import (
    SESSION_KEY,
    clear_batch_import_session,
    create_blog_posts_from_batch,
    load_batch_from_session,
    parse_blog_batch_json,
)


class PreviewSections(list):
    def all(self):
        return self


def build_preview_article(*, title, summary, read_time_minutes, sections, slug="preview"):
    preview_sections = PreviewSections(
        [
            SimpleNamespace(
                heading=section["heading"],
                body=section["body"],
                order=section["order"],
            )
            for section in sections
        ]
    )
    return SimpleNamespace(
        title=title,
        summary=summary,
        read_time_minutes=read_time_minutes,
        created_at=timezone.now(),
        updated_at=timezone.now(),
        sections=preview_sections,
        slug=slug,
        card_summary=summary or "",
    )


class BlogSectionInline(admin.StackedInline):
    model = BlogSection
    extra = 1
    fields = ("order", "heading", "body")
    ordering = ("order", "id")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    change_list_template = "admin/app/blogpost/change_list.html"
    change_form_template = "admin/app/blogpost/change_form.html"
    form = BlogPostAdminForm
    list_display = ("title", "status", "read_time_minutes", "slug", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("title", "summary", "sections__heading", "sections__body")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = [BlogSectionInline]
    save_on_top = True
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "status",
                    "read_time_minutes",
                    "summary",
                )
            },
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "bulk-import/",
                self.admin_site.admin_view(self.bulk_import_view),
                name="app_blogpost_bulk_import",
            ),
            path(
                "bulk-import/preview/",
                self.admin_site.admin_view(self.bulk_import_preview_view),
                name="app_blogpost_bulk_import_preview",
            ),
            path(
                "bulk-import/confirm/",
                self.admin_site.admin_view(self.bulk_import_confirm_view),
                name="app_blogpost_bulk_import_confirm",
            ),
            path(
                "bulk-import/cancel/",
                self.admin_site.admin_view(self.bulk_import_cancel_view),
                name="app_blogpost_bulk_import_cancel",
            ),
            path(
                "page-preview/",
                self.admin_site.admin_view(self.page_preview_view),
                name="app_blogpost_page_preview",
            ),
        ]
        return custom_urls + urls

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context["bulk_import_url"] = reverse("admin:app_blogpost_bulk_import")
        return super().changelist_view(request, extra_context=extra_context)

    def bulk_import_view(self, request):
        clear_batch_import_session(request)

        if request.method == "POST":
            form = BlogBatchUploadForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    batch = parse_blog_batch_json(form.cleaned_data["batch_file"])
                except ValidationError as exc:
                    form.add_error("batch_file", exc.message)
                else:
                    request.session[SESSION_KEY] = batch.to_session()
                    request.session.modified = True
                    return redirect("admin:app_blogpost_bulk_import_preview")
        else:
            form = BlogBatchUploadForm()

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Bulk import blog posts",
            "form": form,
            "back_url": reverse("admin:app_blogpost_changelist"),
        }
        return render(request, "admin/app/blogpost/bulk_import.html", context)

    def bulk_import_preview_view(self, request):
        try:
            batch = load_batch_from_session(request)
        except ValidationError as exc:
            self.message_user(request, exc.message, level=messages.ERROR)
            return redirect("admin:app_blogpost_bulk_import")

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "Preview bulk blog import",
            "batch": batch,
            "confirm_url": reverse("admin:app_blogpost_bulk_import_confirm"),
            "cancel_url": reverse("admin:app_blogpost_bulk_import_cancel"),
            "page_preview_url": reverse("admin:app_blogpost_page_preview"),
        }
        return render(request, "admin/app/blogpost/bulk_import_preview.html", context)

    def bulk_import_confirm_view(self, request):
        if request.method != "POST":
            return HttpResponseRedirect(reverse("admin:app_blogpost_bulk_import_preview"))

        try:
            batch = load_batch_from_session(request)
            created_posts = create_blog_posts_from_batch(batch)
        except ValidationError as exc:
            self.message_user(request, exc.message, level=messages.ERROR)
            return redirect("admin:app_blogpost_bulk_import")
        except Exception as exc:
            self.message_user(
                request,
                f"Import failed: {exc}",
                level=messages.ERROR,
            )
            return redirect("admin:app_blogpost_bulk_import_preview")

        clear_batch_import_session(request)
        self.message_user(
            request,
            format_html(
                "Imported {} blog post{} successfully.",
                len(created_posts),
                "" if len(created_posts) == 1 else "s",
            ),
            level=messages.SUCCESS,
        )
        return redirect("admin:app_blogpost_changelist")

    def bulk_import_cancel_view(self, request):
        clear_batch_import_session(request)
        self.message_user(request, "Bulk import was cancelled.", level=messages.INFO)
        return redirect("admin:app_blogpost_changelist")

    def render_change_form(self, request, context, *args, **kwargs):
        context["page_preview_url"] = reverse("admin:app_blogpost_page_preview")
        return super().render_change_form(request, context, *args, **kwargs)

    @xframe_options_exempt
    def page_preview_view(self, request):
        batch_index = request.GET.get("batch_index")
        if batch_index is not None:
            try:
                batch = load_batch_from_session(request)
                post = batch["posts"][int(batch_index)]
            except (ValidationError, ValueError, IndexError, TypeError):
                placeholder_article = build_preview_article(
                    title="Preview unavailable",
                    summary="The selected batch preview could not be loaded.",
                    read_time_minutes=5,
                    sections=[],
                )
            else:
                placeholder_article = build_preview_article(
                    title=post["title"],
                    summary=post["summary"],
                    read_time_minutes=post["read_time_minutes"],
                    sections=post["sections"],
                    slug=post["slug"],
                )
        else:
            placeholder_article = build_preview_article(
                title="Untitled blog post",
                summary="",
                read_time_minutes=5,
                sections=[],
            )
        return render(
            request,
            "app/blog_article_page.html",
            {
                "article": placeholder_article,
                "preview_mode": True,
            },
        )


@admin.register(BlogSection)
class BlogSectionAdmin(admin.ModelAdmin):
    list_display = ("heading", "post", "order")
    list_filter = ("post",)
    search_fields = ("heading", "body", "post__title")
    ordering = ("post", "order", "id")
