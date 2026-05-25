from django.contrib import admin
from .models import BlogPost, BlogSection


class BlogSectionInline(admin.StackedInline):
    model = BlogSection
    extra = 1
    fields = ("order", "heading", "body")
    ordering = ("order", "id")


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at", "updated_at")
    search_fields = ("title", "summary", "sections__heading", "sections__body")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = [BlogSectionInline]
    save_on_top = True


@admin.register(BlogSection)
class BlogSectionAdmin(admin.ModelAdmin):
    list_display = ("heading", "post", "order")
    list_filter = ("post",)
    search_fields = ("heading", "body", "post__title")
    ordering = ("post", "order", "id")
