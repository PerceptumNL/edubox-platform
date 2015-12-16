# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0002_auto_20151208_1259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clickedevent',
            name='article',
        ),
        migrations.RemoveField(
            model_name='clickedevent',
            name='word',
        ),
        migrations.RemoveField(
            model_name='ratedevent',
            name='article',
        ),
        migrations.RemoveField(
            model_name='readevent',
            name='article',
        ),
        migrations.RemoveField(
            model_name='scoredevent',
            name='article',
        ),
        migrations.RemoveField(
            model_name='verb',
            name='key',
        ),
        migrations.AddField(
            model_name='clickedevent',
            name='obj',
            field=models.URLField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='clickedevent',
            name='page',
            field=models.URLField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='genericevent',
            name='obj',
            field=models.URLField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='ratedevent',
            name='obj',
            field=models.URLField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='readevent',
            name='obj',
            field=models.URLField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scoredevent',
            name='obj',
            field=models.URLField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='clickedevent',
            name='verb',
            field=models.URLField(max_length=255),
        ),
        migrations.AlterField(
            model_name='genericevent',
            name='verb',
            field=models.URLField(max_length=255),
        ),
        migrations.AlterField(
            model_name='ratedevent',
            name='verb',
            field=models.URLField(max_length=255),
        ),
        migrations.AlterField(
            model_name='readevent',
            name='verb',
            field=models.URLField(max_length=255),
        ),
        migrations.AlterField(
            model_name='scoredevent',
            name='verb',
            field=models.URLField(max_length=255),
        ),
    ]
