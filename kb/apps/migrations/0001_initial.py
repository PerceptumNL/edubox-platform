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
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('root', models.CharField(max_length=255, verbose_name='URL/URLconf')),
                ('identical_urls', models.CharField(max_length=255, blank=True)),
                ('secure', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=255)),
                ('icon', models.URLField(null=True, blank=True)),
                ('users', models.ManyToManyField(related_name='apps', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
