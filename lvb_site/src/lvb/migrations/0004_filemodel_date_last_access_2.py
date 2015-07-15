# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('lvb', '0003_auto_20150322_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='filemodel',
            name='date_last_access_2',
            field=models.DateTimeField(default=datetime.datetime(2015, 3, 29, 21, 0, 32, 241190, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
