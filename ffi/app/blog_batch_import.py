import json
from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import transaction
from django.template.defaultfilters import slugify

from .models import BlogPost, BlogSection


MAX_POSTS_PER_BATCH = 10
MAX_JSON_SIZE_BYTES = 2 * 1024 * 1024
SESSION_KEY = "blog_batch_import"


@dataclass
class ParsedBlogBatch:
    batch_status: str
    business_name: str
    business_location: str
    schema_version: str
    posts: list[dict]

    def to_session(self):
        return {
            "batch_status": self.batch_status,
            "business_name": self.business_name,
            "business_location": self.business_location,
            "schema_version": self.schema_version,
            "posts": self.posts,
        }


def clear_batch_import_session(request):
    request.session.pop(SESSION_KEY, None)


def load_batch_from_session(request):
    batch = request.session.get(SESSION_KEY)
    if not batch:
        raise ValidationError("No staged blog batch was found. Please upload the JSON file again.")
    return batch


def _normalize_status(value, *, fallback):
    candidate = (value or fallback or BlogPost.Status.DRAFT).strip().lower()
    valid_values = {choice for choice, _label in BlogPost.Status.choices}
    if candidate not in valid_values:
        raise ValidationError(f"Unsupported post status '{value}'.")
    return candidate


def _build_unique_slug(raw_slug, title, reserved_slugs):
    base_slug = slugify(raw_slug or title) or "blog-entry"
    candidate = base_slug
    suffix = 2

    while candidate in reserved_slugs or BlogPost.objects.filter(slug=candidate).exists():
        candidate = f"{base_slug}-{suffix}"
        suffix += 1

    reserved_slugs.add(candidate)
    return candidate


def parse_blog_batch_json(uploaded_file):
    payload = _load_json_payload(uploaded_file)
    return _parse_batch_payload(payload)


def _load_json_payload(uploaded_file):
    if uploaded_file.size > MAX_JSON_SIZE_BYTES:
        raise ValidationError("The JSON file is too large. Keep it under 2 MB.")

    try:
        return json.loads(uploaded_file.read().decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValidationError("The uploaded file must be valid UTF-8 JSON.") from exc
    except json.JSONDecodeError as exc:
        raise ValidationError("The uploaded file must contain valid JSON.") from exc


def _parse_batch_payload(payload):
    if not isinstance(payload, dict):
        raise ValidationError("The uploaded JSON must be an object at the top level.")

    posts = payload.get("posts")
    if not isinstance(posts, list) or not posts:
        raise ValidationError("The JSON file must include a non-empty posts array.")
    if len(posts) > MAX_POSTS_PER_BATCH:
        raise ValidationError("A batch can include at most 10 posts.")

    batch_status = _normalize_status(
        payload.get("batch_status"),
        fallback=BlogPost.Status.DRAFT,
    )
    reserved_slugs = set()
    parsed_posts = []

    for index, post_data in enumerate(posts, start=1):
        if not isinstance(post_data, dict):
            raise ValidationError(f"Post #{index} is not a valid object.")

        title = (post_data.get("title") or "").strip()
        if not title:
            raise ValidationError(f"Post #{index} is missing a title.")

        slug = _build_unique_slug(post_data.get("slug"), title, reserved_slugs)
        summary = (post_data.get("summary") or "").strip()
        status = _normalize_status(post_data.get("status"), fallback=batch_status)
        read_time_minutes = post_data.get("read_time_minutes", 5)
        if not isinstance(read_time_minutes, int) or read_time_minutes < 1:
            raise ValidationError(f"Post '{title}' must include a valid read_time_minutes value.")

        sections = post_data.get("blog_sections")
        if not isinstance(sections, list) or not sections:
            raise ValidationError(f"Post '{title}' must include at least one blog section.")

        parsed_sections = []
        seen_orders = set()
        for section_index, section_data in enumerate(sections, start=1):
            if not isinstance(section_data, dict):
                raise ValidationError(
                    f"Post '{title}' section #{section_index} is not a valid object."
                )

            order = section_data.get("order", section_index)
            if not isinstance(order, int) or order < 1:
                raise ValidationError(
                    f"Post '{title}' section #{section_index} has an invalid order value."
                )
            if order in seen_orders:
                raise ValidationError(f"Post '{title}' contains duplicate section order values.")
            seen_orders.add(order)

            heading = (section_data.get("heading") or "").strip()
            body = (section_data.get("body") or "").strip()
            if not heading:
                raise ValidationError(f"Post '{title}' section #{section_index} is missing a heading.")
            if not body:
                raise ValidationError(f"Post '{title}' section #{section_index} is missing body text.")

            parsed_sections.append(
                {
                    "order": order,
                    "heading": heading,
                    "body": body,
                    "preview_excerpt": body[:220].strip(),
                }
            )

        parsed_sections.sort(key=lambda section: (section["order"], section["heading"]))

        parsed_posts.append(
            {
                "title": title,
                "slug": slug,
                "summary": summary,
                "status": status,
                "read_time_minutes": read_time_minutes,
                "section_count": len(parsed_sections),
                "sections": parsed_sections,
            }
        )

    return ParsedBlogBatch(
        batch_status=batch_status,
        schema_version=(payload.get("schema_version") or "").strip(),
        business_name=(payload.get("business_name") or "").strip(),
        business_location=(payload.get("business_location") or "").strip(),
        posts=parsed_posts,
    )


def create_blog_posts_from_batch(batch):
    with transaction.atomic():
        created_posts = []
        for post_data in batch["posts"]:
            post = BlogPost.objects.create(
                title=post_data["title"],
                slug=post_data["slug"],
                summary=post_data["summary"],
                status=BlogPost.Status.PUBLISHED,
                read_time_minutes=post_data["read_time_minutes"],
            )

            BlogSection.objects.bulk_create(
                [
                    BlogSection(
                        post=post,
                        order=section["order"],
                        heading=section["heading"],
                        body=section["body"],
                    )
                    for section in post_data["sections"]
                ]
            )
            created_posts.append(post)

    return created_posts
