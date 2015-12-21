# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apps', '__first__'),
        ('groups', '__first__'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClickedEvent',
            fields=[
                ('uuid', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('page', models.URLField(max_length=255)),
                ('app', models.ForeignKey(to='apps.App')),
                ('group', models.ForeignKey(to='groups.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GenericEvent',
            fields=[
                ('uuid', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.UUIDField()),
                ('app', models.ForeignKey(to='apps.App')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('group', models.ForeignKey(to='groups.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RatedEvent',
            fields=[
                ('uuid', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('app', models.ForeignKey(to='apps.App')),
                ('group', models.ForeignKey(to='groups.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReadEvent',
            fields=[
                ('uuid', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(to='apps.App')),
                ('group', models.ForeignKey(to='groups.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ScoredEvent',
            fields=[
                ('uuid', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('app', models.ForeignKey(to='apps.App')),
                ('group', models.ForeignKey(to='groups.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Verb',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('event_class', models.CharField(max_length=255)),
                ('iri', models.URLField()),
                ('description', models.TextField()),
            ],
        ),
    ]
