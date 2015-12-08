# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('router', '0001_initial'),
        ('news', '0002_auto_20150624_1255'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClickedEvent',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('word', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GenericEvent',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.UUIDField()),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RatedEvent',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ReadEvent',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ScoredEvent',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, default=uuid.uuid4, serialize=False, editable=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('app', models.ForeignKey(to='router.App')),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
            ],
            options={
                'ordering': ['-timestamp'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Verb',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=255)),
                ('event_class', models.CharField(max_length=255)),
                ('iri', models.URLField()),
                ('description', models.TextField()),
            ],
        ),
    ]
