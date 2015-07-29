# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('news', '0002_auto_20150624_1255'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('loader', '0005_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='Context',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('group', models.CharField(max_length=255)),
                ('app', models.ForeignKey(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('uuid', models.UUIDField(serialize=False, primary_key=True, default=uuid.uuid4, editable=False)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('authority', models.CharField(max_length=255)),
                ('version', models.CharField(max_length=255)),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Verb',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('key', models.CharField(max_length=255)),
                ('event_class', models.CharField(max_length=255)),
                ('iri', models.URLField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ClickedEvent',
            fields=[
                ('event_ptr', models.OneToOneField(primary_key=True, parent_link=True, serialize=False, to='events.Event', auto_created=True)),
                ('word', models.CharField(max_length=255)),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
            ],
            options={
                'abstract': False,
            },
            bases=('events.event',),
        ),
        migrations.CreateModel(
            name='RatedEvent',
            fields=[
                ('event_ptr', models.OneToOneField(primary_key=True, parent_link=True, serialize=False, to='events.Event', auto_created=True)),
                ('rating', models.IntegerField()),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
            ],
            options={
                'abstract': False,
            },
            bases=('events.event',),
        ),
        migrations.CreateModel(
            name='ReadEvent',
            fields=[
                ('event_ptr', models.OneToOneField(primary_key=True, parent_link=True, serialize=False, to='events.Event', auto_created=True)),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
            ],
            options={
                'abstract': False,
            },
            bases=('events.event',),
        ),
        migrations.CreateModel(
            name='ScoredEvent',
            fields=[
                ('event_ptr', models.OneToOneField(primary_key=True, parent_link=True, serialize=False, to='events.Event', auto_created=True)),
                ('rating', models.IntegerField()),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
            ],
            options={
                'abstract': False,
            },
            bases=('events.event',),
        ),
        migrations.AddField(
            model_name='event',
            name='context',
            field=models.ForeignKey(to='events.Context'),
        ),
        migrations.AddField(
            model_name='event',
            name='polymorphic_ctype',
            field=models.ForeignKey(to='contenttypes.ContentType', related_name='polymorphic_events.event_set+', editable=False, null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='verb',
            field=models.ForeignKey(to='events.Verb'),
        ),
    ]
