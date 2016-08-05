#!/usr/bin/python3.4
# -*-coding:Utf-8 -*
'''program for manage blender rendering task'''
import os
import xml.etree.ElementTree as xmlMod
from log import *
from save import *
from Preferences.Preferences import *
from TaskList.TaskList import *
from usefullFunctions import now



try:
	# init log string and get script path
	start = now(False)
	log = 'Openning of Blender Render Manager\n'+start+' session.\n'
	scriptPath = os.path.realpath(__file__+'/..')
	
	
	
	# check if configuration and log directories exist, otherwise create it 
	if not os.path.exists('/home/'+os.getlogin()+'/.BlenderRenderManager/log'):
		log += 'No configuration or log directory, create it: fail.'
		os.makedirs('/home/'+os.getlogin()+'/.BlenderRenderManager/log/')
		log = log[:len(log)-5]+'done.\n'
	else:
		log += 'Log and configuration directorie finded.\n'
	
	# use configuration directorie as command working directory
	os.chdir('/home/'+os.getlogin()+'/.BlenderRenderManager/')
	
	# create a log file
	log = Log(start,log)
except Exception as e :
	print(log)
	print(e)


try:
	# check if lock file exist
	log += 'Check lock file :'
	if os.path.exists(os.getcwd()+'/lock'):
		log += '  lock file exist :'
		
		# get info about the last blender manager session (PID and PWD)
		with open(os.getcwd()+'/lock','r') as lockFile:
			processInfo = lockFile.read( ).split('\n')
		PID = processInfo[0]
		PWD = processInfo[1]
		log += '    Last session PID : '+PID+''
		
		# check if there is still a Blender-Render-Manager process with this PID
		if os.path.exists('/proc/'+PID+'/'):
			with open('/proc/'+PID+'/environ','r') as lockFile:
				PWDCount = lockFile.read( ).count('PWD='+PWD)
			if PWDCount > 0:
				log.error('    Another session of Blender-Render-Manager is still working! check '+PID+' PID process and stop it!')
				quit()
		else:
			log += '    No old remaining Blender-Render-Manager session detected.'
	else:
		log += '  No lock file detected.'
	
	# create a lock file to prevent multiple call to the script
	log += '  Create a lock file.'
	with open(os.getcwd()+'/lock','w') as lockFile:
		lockFile.write(str(os.getpid())+'\n'+scriptPath)
	
	
	
	
	# load or create Preferences file
	if not os.path.exists(os.getcwd()+'/preferences'):
		log.write('Create a default preferences file : ','')
		preferences = Preferences()
		savePreferences(preferences)
		log += 'done'
	else:
		log.write('Load saved preferences : ','')
		with open(os.getcwd()+'/preferences','r') as prefFile:
			preferences = Preferences( xmlMod.fromstring( (prefFile.read( ) ) ) )
		log += 'done'
	
	
	
	# check working directory
	if not os.path.exists(preferences.output.path):
		log.write('Can\'t find working directory. Try to create it:','')
		os.makedirs(preferences.output.path)
		log += 'done'
	
	
	
	
	# load or create task list file
	if not os.path.exists(preferences.output.path+'Tasks'):
		log.write('Create empty task list file : ', '')
		tasks = TaskList()
		saveTasks(preferences.output.path, tasks)
		log.write('done')
	else:
		log.write('Load saved task list : ', '')
		with open(preferences.output.path+'Tasks','r') as taskFile:
			tasks = TaskList( xmlMod.fromstring( (taskFile.read( ) ) ) )
		log.write('done')
	
	
	
	tasks.menu(scriptPath, log, preferences)
	checkLogLimit(preferences.logLimit)
	
except Exception as e:
	log.print(False)
	print('Blender-Render-Manager crash in menu : ')
	log.printMenu()
	print('Blender-Render-Manager encounter the exception : '+str(e))


