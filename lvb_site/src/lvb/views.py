from django.shortcuts import render
from lvb.models import FileModel, Privacy
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from constants.Constants import Constants
from SGE.processSGE import clProcessSGE
from django.views import generic
from django.utils import timezone
from django.utils.encoding import smart_str
from django.core.servers.basehttp import FileWrapper
from .forms import UploadFileForm, RadioButtons
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import os, mimetypes


def index(request, sz_error = ""):
	sz_error_file = ""

	constants = Constants()
	file_model = FileModel()
	radioButtons = RadioButtons()
	
	### set privacy options 
	if (request.session.has_key(Constants.TAG_SESSION_OPTION_SELECT)):
		radioButtons.fields['choice_field'].initial = request.session[Constants.TAG_SESSION_OPTION_SELECT] 
	else: radioButtons.fields['choice_field'].initial = "2"
	if (request.session.has_key(Constants.TAG_SESSION_EMAIL)):
		file_model.email = request.session[Constants.TAG_SESSION_EMAIL]
	
	### set info privacy
	file_model.n_privacy_options_id = int(radioButtons.fields['choice_field'].initial) - 1
	if (file_model.n_privacy_options_id == 1):
		sz_info_privacy = Privacy.CHOICES[file_model.n_privacy_options_id][1]
	else: sz_info_privacy = Privacy.CHOICES[file_model.n_privacy_options_id][1]

	### replace information
	if (sz_info_privacy.find("We keep your analysis and") == 0):
		sz_info_privacy = sz_info_privacy.replace("We keep your analysis and", "By default, we keep your analysis and")

	if (request.POST.has_key('example')):
		file_model.sz_sequences = ">Species_1\n---AAAAAAAAAAAaaaaAAAAAAAAA\n"\
									">Species_2\n---AAAAAAAAAAAaaaaAAAAAAAAG\n"\
									">Species_3\nAAAAAAAAAAAAAAaaaaAAAAAaATg\n"\
									">Species_4\nAAAAAAAAAAAAAAAAAAAAAAnaCTg\n"\
									">Species_5\nAAAAAAAAAAAAAAAAAAAAAANUCTG\n"\
									">Species_6\nAAAAAAAAAAAAAAAAAAAAAAAUCTG\n"
	elif (request.POST.has_key('clean')):
		file_model.sz_sequences = ""
	elif (request.POST.has_key('submit') or request.POST.has_key('upload')):	### test if the data is fast and all lines has the same size
		
		sz_file = ""
		b_test = True
		## https://docs.djangoproject.com/en/1.7/topics/http/file-uploads/
		if (request.POST.has_key('upload')): ### by file
			form = UploadFileForm(request.POST, request.FILES)
			if form.is_valid():
				file_model.file_name = str(request.FILES['file'])
				sz_file = constants.get_file_name(Constants.PATH_TEMP, Constants.FILE_TAG_TEMP, "")
				(b_test, sz_error_file) = constants.save_file_disk(sz_file, request.FILES['file'])
				if (b_test): (b_test, sz_error_file) = constants.is_fasta(sz_file)
			else:
				sz_error_file = "Error: choose a FASTA file, please..."
				b_test = False
		else:		### sequence posted
			sz_file = constants.get_file_name(Constants.PATH_TEMP, Constants.FILE_TAG_TEMP, "")
			file_model.sz_sequences = request.POST['sequence'].replace(" ", "")
			handle = open(sz_file, "w")
			handle.write(file_model.sz_sequences)
			handle.close()

			## test fasta
			(b_test, sz_error) = constants.is_fasta(sz_file)

		if (b_test):
			(b_test, sz_error, n_species, n_length_sequences) = constants.is_accept_more_species_length(sz_file)
			if (b_test):
				#### submit file to SGE
				submit = clProcessSGE()
				file_model_temp = FileModel()
				
				## get a unique ID for the job...
				n_count = 0
				while 1:
					(file_model.key_id, file_model.hash_id) = constants.get_key_and_hash(sz_file, file_model.hash_id)
					n_count += 1
					if (n_count > 10):
						file_model.key_id = "" 
						break
					sz_composed_key = "%s_%s" % (file_model.key_id, file_model.hash_id)
					if (not file_model_temp.__class__.objects.filter(key_id=sz_composed_key).exists()):
						file_model.key_id = sz_composed_key
						break
				
				## submit the job
				if (len(file_model.key_id) > 0):
					(b_fail, sz_error) = submit.submit_sge(sz_file, file_model, Constants.PATH_LVB_SGE_WORK_DIRECTORY)
					if (not b_fail):
						file_model.path_job = file_model.key_id
						file_model.n_species = n_species
						file_model.n_length_sequences = n_length_sequences
						file_model.save()
						request.session[Constants.TAG_SESSION_KEY_ID] = file_model.key_id
						constants.remove_file(sz_file) 
						return HttpResponseRedirect(reverse('lvb:result', args=(file_model.key_id,)))
				else:
					sz_error = "Some problem with he server. Please, try again..."
		constants.remove_file(sz_file)
	else:
		file_model.sz_sequences = ""
	
	## to not reload the page
	file_model.is_finished = True
	return render(request, 'lvb/index.html', {'file_model': file_model, 'radioButtons': radioButtons,
			'lvb': "xpto", 'error_message': sz_error, 'error_message_file': sz_error_file, 
			'sz_info_privacy' : sz_info_privacy} )


class ResultsView(generic.DetailView):
	model = FileModel()
	template_name = 'lvb_mvc/results.html'
	
	def get_context_data(self, **kwargs):
		context = super(ResultsView, self).get_context_data(**kwargs)
		context['sz_sequences'] = "xpto sz_sequences" 
		return context

## if you send via SMTP to mailhost on port 25, you shouldnt need a password
def send_email(request, key_id, sz_to_email):
	(sz_error, sz_info) = ("", "")
	if (lvb_validate_email(sz_to_email)):
		n_return = send_mail('LVB job ID', "", 'bioinformatics@st-andrews.ac.uk',
				[sz_to_email], fail_silently=False, html_message="<p>Dear LVB user,</p><p>To retrieve the results of your LVB analysis, follow this link:</p>"\
				"<p><a href=http://lvb.st-andrews.ac.uk/lvb/result/%s>http://lvb.st-andrews.ac.uk/lvb/result/%s</a>"\
				"</p><p>All the best,</p><p>Biotinformatics team at St Andrews University</p>" % (key_id, key_id))
		if (n_return == 0): sz_error = "Error: fail to send email to '%s'" % (sz_to_email)
		else: sz_info = "Email was send to '%s'" % (sz_to_email)
	else:
		sz_error = "Error: failed email validation'%s'" % (request.POST["sendEmailData"])

	file_model_temp = FileModel()
	key_id = key_id.strip()
	query_set = file_model_temp.__class__.objects.filter(key_id=key_id)
	if (len(query_set) == 0):
		return result_empty(request, key_id, "Error: some error with this key...")
	file_model = query_set[0]
	is_reload_page = not file_model.is_finished
	return render(request, 'lvb/result.html', {'file_model': file_model, 'result': "xpto", 'sz_info' : sz_info, 'error_message_email' : sz_error, 'is_reload_page' : is_reload_page } )


def result_empty(request, sz_key = "", sz_error = ""):
	if (request.POST.has_key('key_id') or request.session.has_key(Constants.TAG_SESSION_KEY_ID)):
		return result(request, request.POST['key_id'] if request.POST.has_key('key_id') else request.session[Constants.TAG_SESSION_KEY_ID])
	return render(request, 'lvb/result.html', {'get_key' : "xpto", 'result': "xpto",\
				'sz_key' : sz_key, 'error_message' : sz_error} )	## is possible to put a key...


def result(request, key_id):

	## send email
	if (request.POST.has_key('sendEmailData')):
		return send_email(request, key_id, request.POST['sendEmailData'])
	
	is_reload_page = False
	constants = Constants()
	file_model_temp = FileModel()
	key_id = key_id.strip()
	query_set = file_model_temp.__class__.objects.filter(key_id=key_id)
	if (len(query_set) == 0):
		del request.POST['key_id']
		del request.POST['refresh']
		return result_empty(request, key_id, "ID not found, please try other...")
	file_model = query_set[0]
	file_model.date_last_access = file_model.date_last_access_2
	file_model.date_last_access_2 = timezone.now()
	
	## try to detect if is finished,
	if (file_model.is_finished): ## show the results
		pass
	elif (file_model.job_sge_id == 0):	### fail submit job
		## fail submit job
		sz_error = "Fail submit SGE job %s" % (file_model.date_created.strftime("%Y-%m-%d %H:%M"))
		return render(request, 'lvb/result.html', {'file_model': file_model, 'error_message': sz_error, 'result': "xpto"} )	
	else:
		submit = clProcessSGE()
		n_status_sge_id = submit.get_status_process(file_model.job_sge_id)
		if (n_status_sge_id == clProcessSGE.SGE_JOB_ID_FINISH): ## show the results
			file_model.date_finished = constants.get_datetime_stop_sge_job(file_model.key_id)
			if (file_model.date_finished == None):
				sz_error = "Fail to get results from LVb"
				return render(request, 'lvb/result.html', {'file_model': file_model, 'error_message': sz_error, 'result': "xpto", 'is_reload_page' : is_reload_page } )

			(lvb_starting_temperature, lvb_iterations, lvb_length, lvb_trees, lvb_seed) = submit.get_info_from_lvb_result_file(file_model.key_id)
			file_model.lvb_starting_temperature = lvb_starting_temperature
			file_model.lvb_iterations = lvb_iterations
			file_model.lvb_length = lvb_length
			file_model.lvb_trees = lvb_trees
			file_model.lvb_seed = lvb_seed
			file_model.is_finished = True
			request.session[Constants.TAG_SESSION_KEY_ID] = file_model.key_id
		elif (n_status_sge_id == clProcessSGE.SGE_JOB_ID_PROCESSING):
			file_model.is_processing = True
			file_model.is_finished = False
			is_reload_page = True
		elif (n_status_sge_id == clProcessSGE.SGE_JOB_ID_QUEUE):
			file_model.is_processing = True
			file_model.is_finished = False
			is_reload_page = True
	
	## get information about tree
	lvb_message_tree = ""
	lvb_tree_output = ""
	lvb_output = ""
	if (file_model.is_finished):
		if (file_model.lvb_trees == 0):
			lvb_message_tree = "Zero trees founded..."
		elif (file_model.lvb_trees == 1):
			lvb_message_tree = "Only one tree obtained..."
			lvb_tree_output = constants.get_first_tree(file_model.key_id)
		else:
			lvb_message_tree = "%d trees obtained but only the first is visible, You can download all of them..."
			lvb_tree_output = constants.get_first_tree(file_model.key_id)
		lvb_output = constants.get_all_output_lvb(file_model.key_id)
	file_model.save()
	return render(request, 'lvb/result.html', {'file_model': file_model, 'result': "xpto", 'lvb_message_tree' : lvb_message_tree,
						'lvb_tree_output' : lvb_tree_output, 'lvb_output' : lvb_output, 'is_reload_page' : is_reload_page } )


def other_option(request):
	request.session[Constants.TAG_SESSION_OPTION_SELECT] = request.POST["choice_field"]
	if (lvb_validate_email(request.POST["sendEmailData"])):
		request.session[Constants.TAG_SESSION_EMAIL] = request.POST["sendEmailData"]
	else:
		sz_error = "Error: failed email validation'%s'" % (request.POST["sendEmailData"])
	return index(request, sz_error)


def contact(request):
	return render(request, 'lvb/contact.html', {'contact': "xpto"} )


def about(request):
	return render(request, 'lvb/about.html', {'about': "xpto"} )


def result_output_lvb(request, key_id): # , **kwargs
	filepath = "%s/%s/%s" % (Constants.PATH_LVB_SGE_WORK_DIRECTORY, key_id, Constants.FILE_NAME_OUT_REPORT_LVB)
	wrapper = FileWrapper(file(filepath))
	content_type = mimetypes.guess_type(filepath)[0]
	response = HttpResponse(wrapper, content_type=content_type)
	response['Content-Disposition'] = 'attachment; filename=LVB_output.txt'
	response['Content-Length'] = os.path.getsize(filepath)
	response['X-Sendfile'] = smart_str(filepath)
	return response


def result_tree_lvb(request, key_id): # , **kwargs
	filepath = "%s/%s/%s" % (Constants.PATH_LVB_SGE_WORK_DIRECTORY, key_id, Constants.FILE_NAME_OUT_TREE_LVB)
	wrapper = FileWrapper(file(filepath))
	content_type = mimetypes.guess_type(filepath)[0]
	response = HttpResponse(wrapper, content_type=content_type)
	response['Content-Disposition'] = 'attachment; filename=Tree_lvb_output.txt'
	response['Content-Length'] = os.path.getsize(filepath)
	response['X-Sendfile'] = smart_str(filepath)
	return response


def lvb_validate_email(sz_email):	
	try:
		validate_email(sz_email)
		return True
	except ValidationError:
		return False

