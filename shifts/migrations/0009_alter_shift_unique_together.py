# Generated by Django 5.1.5 on 2025-02-02 10:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("shifts", "0008_alter_availabledate_month_alter_availabledate_year_and_more"),
        ("staff", "0001_initial"),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="shift",
            unique_together={("staff", "date", "is_test")},
        ),
    ]
