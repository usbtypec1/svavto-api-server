# Generated by Django 5.1.4 on 2024-12-28 15:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shifts', '0003_alter_cartowashadditionalservice_car'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShiftFinishPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_id', models.CharField(max_length=255, verbose_name='file id')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('shift', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shifts.shift', verbose_name='shift')),
            ],
            options={
                'verbose_name': 'shift finish photo',
                'verbose_name_plural': 'shift finish photos',
            },
        ),
    ]
