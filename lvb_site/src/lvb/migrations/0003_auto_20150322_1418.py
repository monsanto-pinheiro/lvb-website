# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lvb', '0002_auto_20150316_1459'),
    ]

    operations = [
        migrations.AddField(
            model_name='filemodel',
            name='job_sge_id',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='filemodel',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='filemodel',
            name='date_finished',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='filemodel',
            name='date_last_access',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
