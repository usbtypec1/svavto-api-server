# Generated by Django 5.1.7 on 2025-03-23 08:28

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shifts', '0013_cartowash_windshield_washer_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShiftCarsThreshold',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.PositiveSmallIntegerField(default=8, help_text='The minimum number of cars that must be transferred during a shift.', verbose_name='Значение')),
            ],
            options={
                'verbose_name': 'Shift cars threshold',
                'verbose_name_plural': 'Shift cars threshold',
            },
        ),
        migrations.AlterField(
            model_name='cartowash',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
