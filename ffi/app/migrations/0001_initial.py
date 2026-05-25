from django.db import migrations, models
import django.db.models.deletion
import app.models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="BlogPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("slug", models.SlugField(blank=True, max_length=255, unique=True)),
                (
                    "summary",
                    models.TextField(blank=True, help_text="Optional short summary shown on the main blog hub."),
                ),
                ("main_image", models.ImageField(blank=True, null=True, upload_to=app.models.blog_image_upload_to)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="BlogSection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("heading", models.CharField(max_length=255)),
                ("body", models.TextField(help_text="Use blank lines to separate paragraphs.")),
                ("order", models.PositiveIntegerField(default=0)),
                (
                    "post",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="sections", to="app.blogpost"),
                ),
            ],
            options={"ordering": ["order", "id"]},
        ),
    ]
