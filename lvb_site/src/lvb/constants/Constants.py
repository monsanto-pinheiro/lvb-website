
import os
from Bio import SeqIO
import random
import subprocess
from datetime import datetime
from django.utils import timezone
import pytz

class Constants(object):
	
	PATH_TEMP 		= "/tmp"
	FILE_TAG_TEMP	= "fasta_site"
	PATH_LVB_SGE_WORK_DIRECTORY = "/home/projects/lvb/sge_work/work_dir"
	PATH_LVB_SOFTWARE = "/home/projects/lvb/sge_work/sge/lvb"
	QUEUE_NAME		= "all.q"
	TAG_SESSION_KEY_ID = "tag_session_key_id"
	TAG_SESSION_OPTION_SELECT = "tag_option_select"
	TAG_SESSION_EMAIL = "tag_email"
	
	## lVB FILE NAMES
	FILE_NAME_OUT_TREE_LVB = "outtree"
	FILE_NAME_INFILE_LVB = "infile"
	FILE_NAME_OUT_REPORT_LVB = "resultLVB.txt"
	
	MAX_SPECIES = 100
	MAX_LENGTH_SEQUENCES = 10000
	MIN_LENGTH_SEQUENCES = 10

	def genKey(self):
		return ''.join(random.choice('0123456789ABCDEFGHIJLKMNOPQRSTUVWXZY') for i in range(6))

	def getStrWithReturn(self, szStrin, nPos):
		nCount = 0
		szStr = ''
		szTemp = szStrin.strip('\n')
		while nCount < len(szTemp):
			if (nCount <> 0): szStr += '\n'
			szStr += szTemp[nCount: nCount +nPos].strip(' ')
			nCount+= nPos
		return szStr
	
	def get_directory(self, path_test, sz_pre_name, sz_post_name, b_make_dir):
		sz_directory = ""
		while 1:
			sz_directory = "%s_%07d%s" % (sz_pre_name, random.randint(999, 9999999), sz_post_name)
			if (len(path_test) > 0):
				if (not os.path.exists(sz_directory)): break
			elif (not os.path.exists(sz_directory)): break
		
		if (b_make_dir == 1):
			cmd = ""
			if (len(path_test) > 0): cmd = "mkdir %s/%s" % (path_test, sz_directory)
			else: cmd = "mkdir %s" % (sz_directory)
			os.system(cmd)
		return sz_directory
	
	def get_file_name(self, path_test, sz_pre_name, sz_post_name = ""):
		while 1:
			sz_file_temp = "%s_%07d%s" % (sz_pre_name, random.randint(999, 9999999), sz_post_name)
			sz_file = sz_file_temp
			if (len(path_test) > 0):
				sz_file = "%s/%s" % (path_test, sz_file_temp)
				if (not os.path.exists(sz_file)): break
			elif (not os.path.exists(sz_file)): break
		return sz_file
	
	def is_fasta(self, sz_file_name):
		handle = open(sz_file_name)
		b_pass = False
		for line in handle:
			sz_temp = line.strip()
			if (len(sz_temp) == 0): continue
			if (sz_temp[0] == ">"): 
				b_pass = True
				break
			else: 
				handle.close()
				return (False, "Error: the data doesn't start with '>'")
		handle.close()
		if (not b_pass): return (False, "Error: there's not data")

		record_dict = SeqIO.index(sz_file_name, "fasta")
		if (len(record_dict) > 0): return (True, "")
		return (False, "Error: the sequence is not in FASTA format")

	def is_accept_more_species_length(self, sz_file_name):
		(n_species, n_length_sequences) = (0, 0)
		
		record_dict = SeqIO.index(sz_file_name, "fasta")
		if (len(record_dict) < 3): return (False, "It is necessary at least 3 species", n_species, n_length_sequences)
		n_species = len(record_dict)
		if (n_species > self.MAX_SPECIES):
			return (False, "The max number for species is %d. You are submitting %d" % (self.MAX_SPECIES, n_species), n_species, n_length_sequences)
		
		## sequences
		n_min = -1
		n_length_sequences = -1
		sz_min_name = ""
		for key in record_dict:
			if (n_min == -1): 
				n_min = len(str(record_dict[key].seq))
				n_length_sequences = n_min
				sz_min_name = record_dict[key].name
			elif (len(str(record_dict[key].seq)) <> n_min): return (False, "The sequences need to have same length between species.\nThe %s and %s has different length" % (record_dict[key].name, sz_min_name), n_species, n_length_sequences)
			
		if (n_length_sequences < self.MIN_LENGTH_SEQUENCES): return (False, "The sequences need to have same at least %d of length." % (self.MIN_LENGTH_SEQUENCES), n_species, n_length_sequences)
		if (n_length_sequences > self.MAX_LENGTH_SEQUENCES): return (False, "The sequences have more than %d of length." % (self.MAX_LENGTH_SEQUENCES), n_species, n_length_sequences)
		return (True, "", n_species, n_length_sequences)

	def remove_file(self, sz_file_name):
		## only remove files from PATH_TEMP directory
		if (len(sz_file_name) == 0): return
		if (os.path.exists(sz_file_name) and sz_file_name.find(self.PATH_TEMP) == 0):
			sz_cmd = "rm %s" % (sz_file_name)
			os.system(sz_cmd)

	def save_file_disk(self, sz_file_dest, file_from_web):
		with open(sz_file_dest, 'wb+') as destination:
			for chunk in file_from_web.chunks():
				destination.write(chunk)
				
		return self.__process_zip_files__(str(file_from_web), sz_file_dest, sz_file_dest)
	
	### it decompress files and return in the same name of dest file
	def __process_zip_files__(self, sz_file_name_from_web, sz_file_in, sz_file_dest, b_remove_in = True):

		vect_ext_gzip = [".gz", ".gzip"]
		vect_ext_zip = [".zip"]
		
		if (not os.path.exists(sz_file_in)): return
		sz_file_dest_temp = self.get_file_name(Constants.PATH_TEMP, Constants.FILE_TAG_TEMP, "")
		sz_cmd = "cp %s %s" % (sz_file_in, sz_file_dest_temp)
		os.system(sz_cmd)

		sz_file_dest_temp_2 = self.get_file_name(Constants.PATH_TEMP, Constants.FILE_TAG_TEMP, "")
		if ((sz_file_name_from_web.find(vect_ext_gzip[0]) > 0 and sz_file_name_from_web.find(vect_ext_gzip[0]) == len(sz_file_name_from_web) - len(vect_ext_gzip[0])) or 
			(sz_file_name_from_web.find(vect_ext_gzip[1]) > 0 and sz_file_name_from_web.find(vect_ext_gzip[1]) == len(sz_file_name_from_web) - len(vect_ext_gzip[1])) ):
			sz_cmd = "gzip -cd %s > %s;" % (sz_file_dest_temp, sz_file_dest_temp_2)
			if (os.system(sz_cmd)):
				self.remove_file(sz_file_dest_temp); self.remove_file(sz_file_dest_temp_2)
				return (False, "Error: some problem to uncompress '" + sz_file_name_from_web) + "'"
			self.remove_file(sz_file_dest_temp);
			sz_file_dest_temp = sz_file_dest_temp_2
		elif (sz_file_name_from_web.find(vect_ext_zip[0]) > 0 and  sz_file_name_from_web.find(vect_ext_zip[0]) == len(sz_file_name_from_web) - len(vect_ext_zip[0])):
			sz_cmd = "unzip -p %s > %s;" % (sz_file_dest_temp, sz_file_dest_temp_2)
			if (os.system(sz_cmd)):
				self.remove_file(sz_file_dest_temp); self.remove_file(sz_file_dest_temp_2)
				return (False, "Error: some problem to uncompress '" + sz_file_name_from_web) + "'"
			self.remove_file(sz_file_dest_temp);
			sz_file_dest_temp = sz_file_dest_temp_2
		
#		vect_mime_types = mimetypes.guess_type(sz_file_in)
#		for type_ in reversed(vect_mime_types):
#			if (type_ == None or type_ == "text/plain"): continue
#			
#			if (type_ == "gzip"):
#				sz_file_dest_temp_2 = self.get_file_name(Constants.PATH_TEMP, Constants.FILE_TAG_TEMP, "")
#				sz_cmd = "gzip -cd %s > %s; rm %s;" % (sz_file_dest_temp, sz_file_dest_temp_2, sz_file_dest_temp)
#				os.system(sz_cmd)
#				sz_file_dest_temp = sz_file_dest_temp_2
#			elif (type_ == "application/zip"):
#				sz_file_dest_temp_2 = self.get_file_name(Constants.PATH_TEMP, Constants.FILE_TAG_TEMP, "")
#				sz_cmd = "unzip -p %s > %s; rm %s;" % (sz_file_dest_temp, sz_file_dest_temp_2, sz_file_dest_temp)
#				os.system(sz_cmd)
#				sz_file_dest_temp = sz_file_dest_temp_2
		
		### copy to final destination...
		sz_cmd = "mv %s %s" % (sz_file_dest_temp, sz_file_dest)
		os.system(sz_cmd)
		
		if (b_remove_in and sz_file_in <> sz_file_dest): self.remove_file(sz_file_in)
		return (True, "")



	def get_key_and_hash(self, sz_file_name, hash_id = ""):
		## only remove files from PATH_TEMP directory
		if (not os.path.exists(sz_file_name)): return ("", "")
		
		if (len(hash_id) == 0):
			sz_cmd = "md5sum " + sz_file_name
			result = subprocess.check_output(sz_cmd, shell=True)
			hash_id = result.split(' ')[0]
		return (self.genKey(), hash_id)

	def get_result_directory(self, key_id):
		return "%s/%s" % (self.PATH_LVB_SGE_WORK_DIRECTORY, key_id)

	def get_datetime_stop_sge_job(self, key_id):
		sz_file = "%s/%s" % (self.get_result_directory(key_id), self.FILE_NAME_OUT_REPORT_LVB)
		if (not os.path.exists(sz_file)): return None
		return timezone.localtime(datetime.fromtimestamp(os.path.getmtime(sz_file), tz=pytz.utc))
	
	def get_first_tree(self, key_id):
		sz_out = ""
		sz_file = "%s/%s" % (self.get_result_directory(key_id), self.FILE_NAME_OUT_TREE_LVB)
		if (not os.path.exists(sz_file)): return sz_out
		handle = open(sz_file)
		for line in handle:
			sz_temp = line.strip()
			if (len(sz_temp) == 0): continue
			sz_out = "<p>" + sz_temp + "</p>\n"
			break
		handle.close() 
		return sz_out

	def get_all_output_lvb(self, key_id):
		sz_out = ""
		sz_text_fine = "cooling schedule"
		sz_file = "%s/%s" % (self.get_result_directory(key_id), self.FILE_NAME_OUT_REPORT_LVB)
		if (not os.path.exists(sz_file)): return sz_out
		
		handle = open(sz_file)
		sz_out = ""
		(b_open, b_data, b_all_line) = (False, False, False)
		for line in handle:
			sz_temp = line.strip()
			if (len(sz_temp) == 0):
				if (b_data):
					sz_out += "</p>"
					b_data = False
					b_open = False
				continue
			
			if (sz_temp.find(sz_text_fine) == 0): b_all_line = True
			if (not b_open): 
				sz_out += '<p class="text-justify">'
				b_open = True
			if (b_all_line): sz_out += line + "<br>"
			else: sz_out += line
			b_data = True
		handle.close()
		if (b_data): sz_out += "</p>"
		return sz_out




