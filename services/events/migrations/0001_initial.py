# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('news', '0002_auto_20150624_1255'),
        ('loader', '0005_service'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClickedEvent',
            fields=[
                ('uuid', models.UUIDField(editable=False, default=uuid.uuid4, serialize=False, primary_key=True)),
                ('group', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('word', models.CharField(max_length=255)),
                ('app', models.ForeignKey(to='loader.App')),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, to='contenttypes.ContentType', related_name='polymorphic_events.clickedevent_set+')),
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
                ('uuid', models.UUIDField(editable=False, default=uuid.uuid4, serialize=False, primary_key=True)),
                ('group', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('object_id', models.PositiveIntegerField()),
                ('app', models.ForeignKey(to='loader.App')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, to='contenttypes.ContentType', related_name='polymorphic_events.genericevent_set+')),
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
                ('uuid', models.UUIDField(editable=False, default=uuid.uuid4, serialize=False, primary_key=True)),
                ('group', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('app', models.ForeignKey(to='loader.App')),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, to='contenttypes.ContentType', related_name='polymorphic_events.ratedevent_set+')),
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
                ('uuid', models.UUIDField(editable=False, default=uuid.uuid4, serialize=False, primary_key=True)),
                ('group', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('app', models.ForeignKey(to='loader.App')),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, to='contenttypes.ContentType', related_name='polymorphic_events.readevent_set+')),
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
                ('uuid', models.UUIDField(editable=False, default=uuid.uuid4, serialize=False, primary_key=True)),
                ('group', models.CharField(max_length=255)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('stored', models.DateTimeField(auto_now_add=True)),
                ('rating', models.IntegerField()),
                ('app', models.ForeignKey(to='loader.App')),
                ('article', models.ForeignKey(to='news.TimestampedArticle')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, null=True, to='contenttypes.ContentType', related_name='polymorphic_events.scoredevent_set+')),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
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
