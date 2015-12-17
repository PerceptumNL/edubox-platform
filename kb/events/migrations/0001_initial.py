# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import uuid
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('kb', '0001_initial'),
        ('usermanagement', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClickedEvent',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('page', models.URLField(max_length=255)),
                ('app', models.ForeignKey(to='kb.App')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
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
                ('uuid', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.UUIDField()),
                ('app', models.ForeignKey(to='kb.App')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
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
                ('uuid', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('app', models.ForeignKey(to='kb.App')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
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
                ('uuid', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(to='kb.App')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
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
                ('uuid', models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4, serialize=False)),
                ('verb', models.URLField(max_length=255)),
                ('obj', models.URLField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('app', models.ForeignKey(to='kb.App')),
                ('group', models.ForeignKey(to='usermanagement.Group')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_class', models.CharField(max_length=255)),
                ('iri', models.URLField()),
                ('description', models.TextField()),
            ],
        ),
    ]
