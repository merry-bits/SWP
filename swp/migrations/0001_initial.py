# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-09 13:01
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('event_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('title', models.CharField(max_length=128)),
                ('event_date', models.DateField()),
                ('description', models.TextField()),
                ('visible', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('image_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('original_file_name', models.CharField(editable=False, max_length=256)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('photo_id', models.BigAutoField(primary_key=True, serialize=False)),
                ('slug', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('caption', models.CharField(max_length=256)),
                ('exif', models.TextField(blank=True, editable=False, null=True)),
                ('model', models.TextField(blank=True, editable=False, null=True)),
                ('exposure', models.TextField(blank=True, editable=False, null=True)),
                ('f_number', models.TextField(blank=True, editable=False, null=True)),
                ('iso_speed', models.TextField(blank=True, editable=False, null=True)),
                ('focal_length_35', models.TextField(blank=True, editable=False, null=True)),
                ('visible', models.BooleanField(default=False)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='swp.Event')),
                ('image', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='photo_image', to='swp.Image')),
                ('original', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='swp.Image')),
            ],
        ),
    ]
