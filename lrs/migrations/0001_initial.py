# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import uuid
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('news', '0002_auto_20150624_1255'),
        ('loader', '0005_service'),
    ]

    operations = [
        migrations.CreateModel(
            name='Context',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('group', models.CharField(max_length=255)),
                ('app', models.ForeignKey(to='loader.App')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('uuid', models.UUIDField(serialize=False, editable=False, default=uuid.uuid4, primary_key=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('key', models.CharField(max_length=255)),
                ('event_class', models.CharField(max_length=255)),
                ('iri', models.URLField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ClickedEvent',
            fields=[
                ('event_ptr', models.OneToOneField(serialize=False, to='lrs.Event', parent_link=True, primary_key=True, auto_created=True)),
                ('word', models.CharField(max_length=255)),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
            ],
            options={
                'abstract': False,
            },
            bases=('lrs.event',),
        ),
        migrations.CreateModel(
            name='RatedEvent',
            fields=[
                ('event_ptr', models.OneToOneField(serialize=False, to='lrs.Event', parent_link=True, primary_key=True, auto_created=True)),
                ('rating', models.IntegerField()),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
            ],
            options={
                'abstract': False,
            },
            bases=('lrs.event',),
        ),
        migrations.CreateModel(
            name='ReadEvent',
            fields=[
                ('event_ptr', models.OneToOneField(serialize=False, to='lrs.Event', parent_link=True, primary_key=True, auto_created=True)),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
            ],
            options={
                'abstract': False,
            },
            bases=('lrs.event',),
        ),
        migrations.CreateModel(
            name='ScoredEvent',
            fields=[
                ('event_ptr', models.OneToOneField(serialize=False, to='lrs.Event', parent_link=True, primary_key=True, auto_created=True)),
                ('rating', models.IntegerField()),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
            ],
            options={
                'abstract': False,
            },
            bases=('lrs.event',),
        ),
        migrations.AddField(
            model_name='event',
            name='context',
            field=models.ForeignKey(to='lrs.Context'),
        ),
        migrations.AddField(
            model_name='event',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, related_name='polymorphic_lrs.event_set+', to='contenttypes.ContentType', null=True),
        ),
        migrations.AddField(
            model_name='event',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='event',
            name='verb',
            field=models.ForeignKey(to='lrs.Verb'),
        ),
    ]
