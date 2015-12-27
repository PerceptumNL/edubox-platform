# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('color', models.CharField(max_length=50, blank=True, default='#f3f3f3')),
                ('order', models.IntegerField(default=0)),
                ('image', models.CharField(max_length=255, null=True, blank=True)),
                ('parent', models.ForeignKey(blank=True, to='news.Category', null=True, related_name='children')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, related_name='polymorphic_news.category_set+')),
            ],
            options={
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='ContentFeed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('feed', models.URLField()),
                ('last_update', models.DateTimeField(null=True, blank=True)),
                ('category', models.ForeignKey(to='news.Category', related_name='feeds')),
                ('polymorphic_ctype', models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, related_name='polymorphic_news.contentfeed_set+')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ContentSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('link', models.URLField(max_length=255)),
                ('logo', models.CharField(max_length=255, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='TimestampedArticle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('publication_date', models.DateTimeField()),
                ('title', models.CharField(max_length=255)),
                ('body', models.TextField(null=True, blank=True)),
                ('image', models.URLField(null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FeedArticle',
            fields=[
                ('timestampedarticle_ptr', models.OneToOneField(primary_key=True, serialize=False, to='news.TimestampedArticle', parent_link=True, auto_created=True)),
                ('identifier', models.URLField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=('news.timestampedarticle',),
        ),
        migrations.AddField(
            model_name='timestampedarticle',
            name='categories',
            field=models.ManyToManyField(to='news.Category', related_name='articles'),
        ),
        migrations.AddField(
            model_name='timestampedarticle',
            name='polymorphic_ctype',
            field=models.ForeignKey(editable=False, to='contenttypes.ContentType', null=True, related_name='polymorphic_news.timestampedarticle_set+'),
        ),
        migrations.AddField(
            model_name='timestampedarticle',
            name='source',
            field=models.ForeignKey(blank=True, to='news.ContentSource', null=True),
        ),
        migrations.AddField(
            model_name='contentfeed',
            name='source',
            field=models.ForeignKey(blank=True, to='news.ContentSource', null=True),
        ),
        migrations.CreateModel(
            name='KidsWeekFeed',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('news.contentfeed',),
        ),
        migrations.CreateModel(
            name='RSSFeed',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('news.contentfeed',),
        ),
        migrations.CreateModel(
            name='SevenDaysFeed',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('news.contentfeed',),
        ),
    ]
