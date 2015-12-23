# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('groups', '0002_auto_20151223_1838'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClickedEvent',
            fields=[
                ('uuid', models.UUIDField(serialize=False, default=uuid.uuid4, editable=False, primary_key=True)),
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
                'abstract': False,
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='GenericEvent',
            fields=[
                ('uuid', models.UUIDField(serialize=False, default=uuid.uuid4, editable=False, primary_key=True)),
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
                'abstract': False,
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='RatedEvent',
            fields=[
                ('uuid', models.UUIDField(serialize=False, default=uuid.uuid4, editable=False, primary_key=True)),
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
                'abstract': False,
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ReadEvent',
            fields=[
                ('uuid', models.UUIDField(serialize=False, default=uuid.uuid4, editable=False, primary_key=True)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(to='apps.App')),
                ('group', models.ForeignKey(to='groups.Group')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ScoredEvent',
            fields=[
                ('uuid', models.UUIDField(serialize=False, default=uuid.uuid4, editable=False, primary_key=True)),
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
                'abstract': False,
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Verb',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('event_class', models.CharField(max_length=255)),
                ('iri', models.URLField()),
                ('description', models.TextField()),
            ],
        ),
    ]
