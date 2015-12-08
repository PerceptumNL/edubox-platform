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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('root', models.CharField(max_length=255, verbose_name='URL/URLconf')),
                ('local', models.BooleanField(default=True)),
                ('identical_urls', models.CharField(max_length=255, blank=True)),
                ('secure', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=255)),
                ('icon', models.URLField(null=True, blank=True)),
                ('users', models.ManyToManyField(related_name='apps', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('root', models.CharField(max_length=255, verbose_name='URL/URLconf')),
                ('local', models.BooleanField(default=True)),
                ('identical_urls', models.CharField(max_length=255, blank=True)),
                ('secure', models.BooleanField(default=True)),
                ('name', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
