# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0003_institute_email_domain'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='group',
            name='tags',
            field=models.ManyToManyField(to='groups.Tag', blank=True),
        ),
    ]
