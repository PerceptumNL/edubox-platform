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
            name='PersistentCookie',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('value', models.CharField(max_length=4096)),
            ],
        ),
        migrations.AddField(
            model_name='app',
            name='persistent_cookies',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='persistentcookie',
            name='app',
            field=models.ForeignKey(to='router.App'),
        ),
        migrations.AddField(
            model_name='persistentcookie',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
