# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('router', '0001_initial'),
        ('events', '0001_initial'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('usermanagement', '0001_initial'),
        ('news', '0002_auto_20150624_1255'),
    ]

    operations = [
        migrations.AddField(
            model_name='scoredevent',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AddField(
            model_name='scoredevent',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='scoredevent',
            name='verb',
            field=models.ForeignKey(to='events.Verb'),
        ),
        migrations.AddField(
            model_name='readevent',
            name='app',
            field=models.ForeignKey(to='router.App'),
        ),
        migrations.AddField(
            model_name='readevent',
            name='article',
            field=models.ForeignKey(to='news.TimestampedArticle'),
        ),
        migrations.AddField(
            model_name='readevent',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AddField(
            model_name='readevent',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='readevent',
            name='verb',
            field=models.ForeignKey(to='events.Verb'),
        ),
        migrations.AddField(
            model_name='ratedevent',
            name='app',
            field=models.ForeignKey(to='router.App'),
        ),
        migrations.AddField(
            model_name='ratedevent',
            name='article',
            field=models.ForeignKey(to='news.TimestampedArticle'),
        ),
        migrations.AddField(
            model_name='ratedevent',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AddField(
            model_name='ratedevent',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ratedevent',
            name='verb',
            field=models.ForeignKey(to='events.Verb'),
        ),
        migrations.AddField(
            model_name='genericevent',
            name='app',
            field=models.ForeignKey(to='router.App'),
        ),
        migrations.AddField(
            model_name='genericevent',
            name='content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='genericevent',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AddField(
            model_name='genericevent',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='genericevent',
            name='verb',
            field=models.ForeignKey(to='events.Verb'),
        ),
        migrations.AddField(
            model_name='clickedevent',
            name='app',
            field=models.ForeignKey(to='router.App'),
        ),
        migrations.AddField(
            model_name='clickedevent',
            name='article',
            field=models.ForeignKey(to='news.TimestampedArticle'),
        ),
        migrations.AddField(
            model_name='clickedevent',
            name='group',
            field=models.ForeignKey(to='usermanagement.Group'),
        ),
        migrations.AddField(
            model_name='clickedevent',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='clickedevent',
            name='verb',
            field=models.ForeignKey(to='events.Verb'),
        ),
    ]
