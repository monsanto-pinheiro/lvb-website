from django import forms
from models import Privacy


class UploadFileForm(forms.Form):
	file = forms.FileField()
	
#	https://docs.djangoproject.com/en/1.7/ref/forms/widgets/
#{% for radio in myform.beatles %}
#    <label for="{{ radio.id_for_label }}">
#        {{ radio.choice_label }}
#        <span class="radio">{{ radio.tag }}</span>
#    </label>
#{% endfor %}

class RadioButtons(forms.Form):
	choice_field = forms.ChoiceField(widget=forms.RadioSelect, choices=Privacy.CHOICES)
	choice_field.choices = (
		(('%s' % (Privacy.PRIVACY_KEEP_ANALYSIS_DATA_EMAIL_CONTACT_FUTURE), Privacy.dt_privacy[Privacy.PRIVACY_KEEP_ANALYSIS_DATA_EMAIL_CONTACT_FUTURE])),
		(('%s' % (Privacy.PRIVACY_KEEP_DATA_LABELS_REMOVED), Privacy.dt_privacy[Privacy.PRIVACY_KEEP_DATA_LABELS_REMOVED])),
		(('%s' % (Privacy.PRIVACY_KEEP_ANALYSIS_DATA_LABELS), Privacy.dt_privacy[Privacy.PRIVACY_KEEP_ANALYSIS_DATA_LABELS])),
		(('%s' % (Privacy.PRIVACY_KEEP_NO_DETAILS_NO_ANALYSIS_NO_DATA), Privacy.dt_privacy[Privacy.PRIVACY_KEEP_NO_DETAILS_NO_ANALYSIS_NO_DATA])), )
	choice_field.initial = "2"
