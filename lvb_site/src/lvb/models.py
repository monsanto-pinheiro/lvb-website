from django.db import models
from django.conf import settings
 

class Privacy(models.Model):
	
	PRIVACY_KEEP_ANALYSIS_DATA_EMAIL_CONTACT_FUTURE = 1
	PRIVACY_KEEP_DATA_LABELS_REMOVED = 2
	PRIVACY_KEEP_ANALYSIS_DATA_LABELS = 3
	PRIVACY_KEEP_NO_DETAILS_NO_ANALYSIS_NO_DATA = 4

	dt_privacy = { 
		PRIVACY_KEEP_ANALYSIS_DATA_EMAIL_CONTACT_FUTURE : 'We keep your analysis, your data and your email address and may contact you in future (e.g. if we find a better way to analyse your data).',
		PRIVACY_KEEP_DATA_LABELS_REMOVED : 'We keep your analysis and your data with the sequence labels removed.',
		PRIVACY_KEEP_ANALYSIS_DATA_LABELS : 'We keep configuration details of your analysis and summary details of your data (e.g. alignment size).',
		PRIVACY_KEEP_NO_DETAILS_NO_ANALYSIS_NO_DATA : 'We keep no details of your analysis or data.',
	}
	CHOICES = (('%s' % (PRIVACY_KEEP_ANALYSIS_DATA_EMAIL_CONTACT_FUTURE), dt_privacy[PRIVACY_KEEP_ANALYSIS_DATA_EMAIL_CONTACT_FUTURE]),
			 ('%s' % (PRIVACY_KEEP_DATA_LABELS_REMOVED), dt_privacy[PRIVACY_KEEP_DATA_LABELS_REMOVED]),
			 ('%s' % (PRIVACY_KEEP_ANALYSIS_DATA_LABELS), dt_privacy[PRIVACY_KEEP_ANALYSIS_DATA_LABELS]),
			 ('%s' % (PRIVACY_KEEP_NO_DETAILS_NO_ANALYSIS_NO_DATA), dt_privacy[PRIVACY_KEEP_NO_DETAILS_NO_ANALYSIS_NO_DATA]), )
	
	description = models.CharField(max_length=1000)
	
# Create your models here.
class FileModel(models.Model):
		
	TAG_FILE_NAME = "data"

	path_job = models.CharField(max_length=1000)				## path where it's running
	file_name = models.CharField(max_length=100)				## file name file in server...
	hash_id = models.CharField(max_length=100)					## hash of the sequences md5
	sz_sequences = models.TextField(max_length=5000)			## max 5000
	key_id = models.CharField(db_index=True, max_length=100)					
	job_sge_id = models.IntegerField(default=0)					## sge job id
	email = models.EmailField()									## email
	date_created = models.DateTimeField(auto_now_add=True, blank=True)			## several kind of dates
	date_finished = models.DateTimeField(auto_now_add=True, blank=True)
	date_last_access = models.DateTimeField(auto_now_add=True, blank=True)
	date_last_access_2 = models.DateTimeField(auto_now_add=True, blank=True)

	is_queue = models.BooleanField(default=False)
	is_processing = models.BooleanField(default=False)
	is_finished = models.BooleanField(default=False)
## need to comment because of migration
	n_privacy_options = models.ForeignKey(Privacy, default=lambda: Privacy.objects.get(id=Privacy.PRIVACY_KEEP_DATA_LABELS_REMOVED))
#	n_privacy_options = models.ForeignKey(Privacy)
	
	n_species = models.IntegerField(default=0)
	n_length_sequences = models.IntegerField(default=0)
	
	lvb_starting_temperature = models.FloatField(default=0)
	lvb_iterations = models.IntegerField(default=0)
	lvb_length = models.IntegerField(default=0)
	lvb_trees = models.IntegerField(default=0)
	lvb_seed = models.IntegerField(default=0)

	def __str__(self):			  # __unicode__ on Python 2
		return self.key_id

