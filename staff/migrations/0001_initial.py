# Generated by Django 5.1.1 on 2024-11-26 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AdminStaff',
            fields=[
                ('id', models.BigIntegerField(db_index=True, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'admin staff',
                'verbose_name_plural': 'admin staff',
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigIntegerField(db_index=True, primary_key=True, serialize=False)),
                ('full_name', models.CharField(max_length=100)),
                ('car_sharing_phone_number', models.CharField(max_length=20)),
                ('console_phone_number', models.CharField(max_length=20)),
                ('banned_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_activity_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'staff',
                'verbose_name_plural': 'staff',
            },
        ),
    ]
