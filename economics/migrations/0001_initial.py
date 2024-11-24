# Generated by Django 5.1.1 on 2024-11-24 17:09

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('staff', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaffServicePrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service', models.CharField(choices=[('comfort_class_car_transfer', 'comfort class car transfer'), ('business_class_car_transfer', 'business class car transfer'), ('van_transfer', 'van transfer'), ('car_transporter_extra_shift', 'car transporter extra shift'), ('urgent_wash', 'urgent wash'), ('item_dry_clean', 'item dry clean')], max_length=255, unique=True)),
                ('price', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Penalty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=255)),
                ('amount', models.PositiveIntegerField()),
                ('consequence', models.CharField(blank=True, choices=[('dismissal', 'dismissal'), ('warn', 'warn')], max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.staff')),
            ],
            options={
                'verbose_name': 'penalty',
                'verbose_name_plural': 'penalties',
            },
        ),
        migrations.CreateModel(
            name='Surcharge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=255)),
                ('amount', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('staff', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='staff.staff')),
            ],
            options={
                'verbose_name': 'surcharge',
                'verbose_name_plural': 'surcharges',
            },
        ),
    ]
