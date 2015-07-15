# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import migrations
from lvb.models import Privacy

def fillInitialData(apps, schema_editor):
	privacy = apps.get_model("lvb", "Privacy")
	if not privacy.objects.filter(pk=Privacy.PRIVACY_KEEP_ANALYSIS_DATA_EMAIL_CONTACT_FUTURE).exists():
		privacy_set = Privacy()
		privacy_set.description = Privacy.dt_privacy[Privacy.PRIVACY_KEEP_ANALYSIS_DATA_EMAIL_CONTACT_FUTURE]
		privacy_set.save()
	if not privacy.objects.filter(pk=Privacy.PRIVACY_KEEP_DATA_LABELS_REMOVED).exists():
		privacy_set = Privacy()
		privacy_set.description = Privacy.dt_privacy[Privacy.PRIVACY_KEEP_DATA_LABELS_REMOVED]
		privacy_set.save()
	if not privacy.objects.filter(pk=Privacy.PRIVACY_KEEP_ANALYSIS_DATA_LABELS).exists():
		privacy_set = Privacy()
		privacy_set.description = Privacy.dt_privacy[Privacy.PRIVACY_KEEP_ANALYSIS_DATA_LABELS]
		privacy_set.save()
	if not privacy.objects.filter(pk=Privacy.PRIVACY_KEEP_NO_DETAILS_NO_ANALYSIS_NO_DATA).exists():
		privacy_set = Privacy()
		privacy_set.description = Privacy.dt_privacy[Privacy.PRIVACY_KEEP_NO_DETAILS_NO_ANALYSIS_NO_DATA]
		privacy_set.save()

class Migration(migrations.Migration):

	dependencies = [
		('lvb', '0001_initial'),
	]

	operations = [
		migrations.RunPython(fillInitialData),
	]
