# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lvb', '0004_filemodel_date_last_access_2'),
    ]

    operations = [
        migrations.AddField(
            model_name='filemodel',
            name='n_length_sequences',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='filemodel',
            name='n_species',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='filemodel',
            name='key_id',
            field=models.CharField(max_length=100, db_index=True),
            preserve_default=True,
        ),
    ]
