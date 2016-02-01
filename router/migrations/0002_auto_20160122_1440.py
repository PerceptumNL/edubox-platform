# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('router', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerCookiejar',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('contents', models.TextField(blank=True, default='{}')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+')),
            ],
        ),
        migrations.RemoveField(
            model_name='servercookie',
            name='user',
        ),
        migrations.DeleteModel(
            name='ServerCookie',
        ),
    ]
