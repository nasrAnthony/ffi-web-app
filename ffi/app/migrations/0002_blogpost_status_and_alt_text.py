from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="main_image_alt_text",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="blogpost",
            name="status",
            field=models.CharField(
                choices=[("draft", "Draft"), ("published", "Published")],
                default="published",
                max_length=20,
            ),
        ),
    ]
