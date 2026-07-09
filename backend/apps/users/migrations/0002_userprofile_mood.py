from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="mood",
            field=models.CharField(
                choices=[
                    ("happy", "Happy"),
                    ("studying", "Studying"),
                    ("slacking", "Slacking"),
                    ("focused", "Focused"),
                    ("tired", "Tired"),
                    ("excited", "Excited"),
                    ("coding", "Coding"),
                ],
                db_index=True,
                default="happy",
                max_length=16,
            ),
        ),
    ]
