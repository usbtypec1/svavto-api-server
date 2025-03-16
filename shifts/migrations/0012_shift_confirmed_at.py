# Generated by Django 5.1.5 on 2025-02-23 18:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("shifts", "0011_shift_rejected_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="shift",
            name="confirmed_at",
            field=models.DateTimeField(
                blank=True, null=True, verbose_name="confirmed at"
            ),
        ),
    ]
