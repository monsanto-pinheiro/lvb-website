# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lvb', '0005_auto_20150331_1128'),
    ]

    operations = [
        migrations.AddField(
            model_name='filemodel',
            name='lvb_iterations',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filemodel',
            name='lvb_length',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filemodel',
            name='lvb_seed',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filemodel',
            name='lvb_starting_temperature',
            field=models.FloatField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filemodel',
            name='lvb_trees',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
