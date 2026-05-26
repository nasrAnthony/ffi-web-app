from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0002_blogpost_status_and_alt_text"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="blogpost",
            name="main_image",
        ),
        migrations.RemoveField(
            model_name="blogpost",
            name="main_image_alt_text",
        ),
    ]
