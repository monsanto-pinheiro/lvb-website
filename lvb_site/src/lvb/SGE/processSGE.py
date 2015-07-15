#!/usr/bin/env python

import os
import time
import commands
from lvb.constants.Constants import Constants


class clProcessSGE:
	
	threadsHead = 5
	szScriptSGEName = "launch_lvb.sh"
	constants = Constants()
	
	SGE_JOB_ID_PROCESSING = 1
	SGE_JOB_ID_QUEUE = 2
	SGE_JOB_ID_FINISH = 3
	
	
	def __init__(self, waitSeconds = 5, szQueueName = Constants.QUEUE_NAME):
		self.waitSeconds = waitSeconds
		self.szQueueName = szQueueName
		
	def submit_sge(self, sz_file, file_model, sz_path_directory):
	
		sz_out_dir = "%s/%s" % (sz_path_directory, file_model.key_id)
		if (not os.path.exists(sz_out_dir)):
			sz_cmd = "mkdir -p " + sz_out_dir
			if (os.system(sz_cmd)): return (True, "Error: fail to create project")
		
		sz_cmd = "cp %s %s/infile" % (sz_file, sz_out_dir)
		if (os.system(sz_cmd)): return (True, "Error: fail to copy fasta file")

		### create bash
		sz_cmd = "cd %s; %s -f fasta -s 509739986 -p %d > %s" % (sz_out_dir, self.constants.PATH_LVB_SOFTWARE, self.threadsHead, self.constants.FILE_NAME_OUT_REPORT_LVB)
		self.setScriptRunSGE(sz_out_dir, sz_cmd)
		n_job_id = int(self.submitteJob(sz_out_dir))
		if (n_job_id == 0):
			file_model.job_sge_id = 0 
			return (True, "Error: fail to submit OGE job")
		file_model.is_queue = True
		file_model.is_processing = False
		file_model.job_sge_id = n_job_id
		file_model.path_job = file_model.key_id
		return (False, "")


	## submitte Job
	def submitteJob(self, sz_out_dir):
		sz_temp = os.getcwd()
		os.chdir(sz_out_dir)	## change dir
		cline = 'qsub %s/%s' % (sz_out_dir, self.szScriptSGEName)
		result = commands.getstatusoutput(cline)
		os.chdir(sz_temp)		## change dir
		if (result[1].find("has been submitted") <> -1):
			return result[1].split()[2]
		return 0


	## create the script to run SGE
	def setScriptRunSGE(self, sz_out_dir, cline, nPriority = 0):
		
		handleSGE = open(sz_out_dir + "/" + self.szScriptSGEName, 'w')
		handleSGE.write("#!/bin/bash\n")
		handleSGE.write("#$ -V\n")	# Specifies  that  all  environment  variables active
									# within the qsub utility be exported to the context of the job.
		handleSGE.write("#$ -S /bin/bash\n") 	# interpreting shell
		handleSGE.write("#$ -j y\n")  # merge the standard error with standard output
		handleSGE.write("#$ -cwd\n")	# execute the job for the current work directory
		handleSGE.write("#$ -q %s\n" % self.szQueueName)	# queue name
		if (nPriority > 0): handleSGE.write("#$ -p %d\n" % (nPriority))	# execute the job for the current work directory
		handleSGE.write("\n" + cline)
		handleSGE.close()
	
		
	## remve file
	def removeFileScriptSGEName(self, bRemoveAllExtension):
		if (os.path.exists(self.szScriptSGEName)):
			if (bRemoveAllExtension == 1):
				cline = "rm %s.*" % (self.szScriptSGEName)
				os.system(cline)
			else: os.remove(self.szScriptSGEName)
	
	## clear all SGE IDs
	def clearJobId(self):
		self.vectJobSGEId = []
		
	## redefenition of wait time
	def setWaitTime(self, waitSeconds):
		self.waitSeconds = waitSeconds

	###
	###		wait for all queue process
	###
	## return 0 if everything OK
	## return other value, error
	def waitToAllEnd(self, dtJobs, szPathAlreadyDone):
		
		while 1:
			time.sleep(self.waitSeconds)		## ten minutes 60*10
			(nReturn, lstDone) = self.__isAllSGEEnd__()
			
			## transfer the done files
			for jobID in lstDone:
				if (dtJobs.has_key(jobID)):
					cmLine = "mv %s %s/%s" %(dtJobs[jobID], szPathAlreadyDone, dtJobs[jobID])
					os.system(cmLine)
			
			## test if is need to continue
			if (nReturn == 0): return 0	## it's done
			elif (nReturn == -1): return nReturn ## error
			
	###
	###		wait for all queue process
	###
	## return 0 if everything OK
	## return other value, error
	def waitToAllEndWithoutMoveFiles(self):
		
		while 1:
			time.sleep(self.waitSeconds)		## ten minutes 60*10
			(nReturn, lstDone) = self.__isAllSGEEnd__()
			
			## test if is need to continue
			if (nReturn == 0): return 0	## it's done
			elif (nReturn == -1): return nReturn ## error

	### test if all jobs submitted to the SGE are finish
	## return 0, if is end
	## return -1, error
	## other value, keeping running
	## also returns a vector with jobId already finish
	def __get_sge_process__(self):

		#Job status - one of
		
		#	* d(eletion)
		#	* E(rror)
		#	* h(old)
		#	* r(unning)
		#	* R(estarted)
		#	* s(uspended),
		#	* S(uspended)
		#	* t(ransfering)
		#	* T(hreshold)
		#	* w(aiting)
		
		tagsSGERunning = ('r', 't')
		tagsSGEWaiting = ('qw', 'w')
		# test with qstat
		szFileResultSGE = self.constants.get_file_name(self.constants.PATH_TEMP, "sge_stat")
		cline = 'qstat > %s' % (szFileResultSGE)
		os.system(cline)
			
		## read the FILE
		handleResult = open(szFileResultSGE)
		vectRunning =[]
		vectWait =[]
		for line in handleResult:
			# pass header and other things
			if (line.find("job-ID") <> -1 or len(line) < 3 or line.find("---") == 0): continue
			if (len(line.split()) > 0):
				## jobid is running
				if (line.split()[4] in tagsSGERunning): vectRunning.append(line.split()[0])
				elif (line.split()[4] in tagsSGEWaiting): vectWait.append(line.split()[0])
		handleResult.close()
		
		## remove file
		cline = 'rm %s' % (szFileResultSGE)
		os.system(cline)
		return (vectRunning, vectWait)

	def get_status_process(self, n_SGE_id):
		(vectRunning, vectWait) = self.__get_sge_process__()
		if (str(n_SGE_id) in vectRunning): return self.SGE_JOB_ID_PROCESSING
		if (str(n_SGE_id) in vectWait): return self.SGE_JOB_ID_QUEUE
		return self.SGE_JOB_ID_FINISH
	
	def get_info_from_lvb_result_file(self, key_id):
		sz_starting_temp = "Starting Temperature is:" 
		sz_seed = "seed                 = "
		sz_iterations = "Rearrangements tried:"
		sz_out_report = "parsimonious tree of length"
		(lvb_starting_temperature, lvb_iterations, lvb_length, lvb_trees, lvb_seed) = (0, 0, 0, 0, 0)
		sz_file_out = "%s/%s/%s" % (self.constants.PATH_LVB_SGE_WORK_DIRECTORY, key_id, self.constants.FILE_NAME_OUT_REPORT_LVB)
		if (not os.path.exists(sz_file_out)): return (lvb_starting_temperature, lvb_iterations, lvb_length, lvb_trees, lvb_seed)
		
		handle = open(sz_file_out)
		for line in handle:
			if (line.find(sz_starting_temp) == 0):
				if (len(line.split(sz_starting_temp)) > 0): lvb_starting_temperature = float(line.split(sz_starting_temp)[1].strip())
			if (line.find(sz_seed) == 0):
				if (len(line.split(sz_seed)) > 0): lvb_seed = int(line.split(sz_seed)[1].strip())
			if (line.find(sz_iterations) == 0):
				if (len(line.split(sz_iterations)) > 0): lvb_iterations = int(line.split(sz_iterations)[1].strip())
			if (line.find(sz_out_report) <> -1):
				if (len(line.split(sz_out_report)) > 1):
					lvb_trees = int(line.split(sz_out_report)[0].strip().split(' ')[0])
					lvb_length = int(line.split(sz_out_report)[1].strip().split(' ')[0])
		handle.close()
		return (lvb_starting_temperature, lvb_iterations, lvb_length, lvb_trees, lvb_seed)

		