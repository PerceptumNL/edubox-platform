# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='App',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('root', models.CharField(verbose_name='URL/URLconf', max_length=255)),
                ('identical_urls', models.CharField(max_length=255, blank=True)),
                ('secure', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=255)),
                ('icon', models.URLField(blank=True, null=True)),
                ('users', models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='apps')),
            ],
        ),
    ]
