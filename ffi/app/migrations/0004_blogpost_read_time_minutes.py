from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0003_remove_blogpost_images"),
    ]

    operations = [
        migrations.AddField(
            model_name="blogpost",
            name="read_time_minutes",
            field=models.PositiveSmallIntegerField(default=5),
        ),
    ]
