# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('loader', '0005_service'),
        ('news', '0002_auto_20150624_1255'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ClickedEvent',
            fields=[
                ('uuid', models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid4, editable=False)),
                ('group', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('word', models.CharField(max_length=255)),
                ('app', models.ForeignKey(to='loader.App')),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, to='contenttypes.ContentType', related_name='polymorphic_events.clickedevent_set+', null=True)),
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
                ('uuid', models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid4, editable=False)),
                ('group', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.UUIDField()),
                ('app', models.ForeignKey(to='loader.App')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, to='contenttypes.ContentType', related_name='polymorphic_events.genericevent_set+', null=True)),
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
                ('uuid', models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid4, editable=False)),
                ('group', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('app', models.ForeignKey(to='loader.App')),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, to='contenttypes.ContentType', related_name='polymorphic_events.ratedevent_set+', null=True)),
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
                ('uuid', models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid4, editable=False)),
                ('group', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(to='loader.App')),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, to='contenttypes.ContentType', related_name='polymorphic_events.readevent_set+', null=True)),
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
                ('uuid', models.UUIDField(primary_key=True, serialize=False, default=uuid.uuid4, editable=False)),
                ('group', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('app', models.ForeignKey(to='loader.App')),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, to='contenttypes.ContentType', related_name='polymorphic_events.scoredevent_set+', null=True)),
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
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('key', models.CharField(max_length=255)),
                ('event_class', models.CharField(max_length=255)),
                ('iri', models.URLField()),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='scoredevent',
            name='verb',
            field=models.ForeignKey(to='events.Verb'),
        ),
        migrations.AddField(
            model_name='readevent',
            name='verb',
            field=models.ForeignKey(to='events.Verb'),
        ),
        migrations.AddField(
            model_name='ratedevent',
            name='verb',
            field=models.ForeignKey(to='events.Verb'),
        ),
        migrations.AddField(
            model_name='genericevent',
            name='verb',
            field=models.ForeignKey(to='events.Verb'),
        ),
        migrations.AddField(
            model_name='clickedevent',
            name='verb',
            field=models.ForeignKey(to='events.Verb'),
        ),
    ]
